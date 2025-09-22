#!/usr/bin/env python3
"""
Burn TikTok Style Subtitles
===========================

Script CLI para "quemar" (hardcode) subtítulos .srt sobre un video con un estilo tipo TikTok
usando únicamente ffmpeg (sin depender de moviepy). Permite:

- Ajustar tamaño de fuente, colores (texto / borde / caja)
- Añadir un fondo tipo caja redondeada semi-transparente detrás del texto (estilo TikTok)
- Forzar formato vertical 9:16 (1080x1920 por defecto) centrando o recortando el video fuente
- Escoger alineación vertical (por defecto: bottom)

Requisitos:
  - ffmpeg compilado con libass (casi todas las distribuciones modernas lo incluyen)
  - Archivo .srt UTF-8 (se recomienda limpiar caracteres problemáticos)

Ejemplos:
  python burn_tiktok_subs.py input.mp4 subs.srt -o output.mp4
  python burn_tiktok_subs.py input.mp4 subs.srt -o output.mp4 --font-size 68 --outline 3
  python burn_tiktok_subs.py input.mp4 subs.srt --tiktok-vertical
  python burn_tiktok_subs.py input.mp4 subs.srt --tiktok-vertical --target-size 720x1280
  python burn_tiktok_subs.py input.mp4 subs.srt --box --box-color 000000@0.5

Notas de estilo TikTok:
  - Letra grande y centrada en la parte inferior (pero no pegada al borde) -> margen inferior ~160px en 1080x1920
  - Contorno negro grueso (outline)
  - Opcional: caja negra translúcida con bordes suaves (libass simula borde redondeado con bordes + blur ligero)

Limitaciones:
  - El render libass no soporta perfectamente blur y borde redondeado combinados en todas las plataformas.
  - Para un estilo avanzado (animaciones palabra a palabra) necesitarías generar ASS dinámico.

Autor: Sistema de Transcripción de Gaming
Fecha: 2025
"""
import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path

# ------------------------------
# Utilidades ASS
# ------------------------------
def build_ass_header(font_name: str, font_size: int, primary_color: str, outline_color: str,
                     outline: int, shadow: int, box: bool, box_color: str, margin_v: int,
                     alignment: int) -> str:
    """Genera cabecera ASS con un único estilo principal.
    Colores en formato ASS: &HAABBGGRR (A=alpha hex invertida). Se recibe primary_color tipo 'FFFFFF' o 'FFFFFF@0.2'
    outline_color igual lógica, box_color para fondo si box=True.
    alignment: 2=bottom-center, 8=top-center, 5=middle-center
    """
    def parse_color(c: str, default_alpha: float=0.0):
        # c: 'RRGGBB' o 'RRGGBB@0.3'
        if '@' in c:
            rgb, a = c.split('@', 1)
            try:
                alpha = float(a)
            except ValueError:
                alpha = default_alpha
        else:
            rgb = c
            alpha = default_alpha
        rgb = rgb.strip().lstrip('#')
        if len(rgb) != 6:
            rgb = 'FFFFFF'
        # ASS usa AA BB GG RR (alpha invertida 00 = opaco, FF = transparente)
        a_hex = f"{int(max(0,min(1,alpha))*255):02X}"  # 00 opaco
        rr = rgb[0:2]
        gg = rgb[2:4]
        bb = rgb[4:6]
        return f"&H{a_hex}{bb}{gg}{rr}"

    primary_ass = parse_color(primary_color, 0.0)
    outline_ass = parse_color(outline_color, 0.0)
    back_ass = parse_color(box_color, 0.6 if box else 1.0) if box else '&HFF000000'  # transparente si no box

    style = ("[Script Info]\n"
             "ScriptType: v4.00+\n"
             "PlayResX: 1080\n"
             "PlayResY: 1920\n"  # Base para escalado; ffmpeg auto reescala si difiere el video
             "WrapStyle: 2\n"
             f"ScaledBorderAndShadow: yes\n"  # hace que outline escale
             "\n[V4+ Styles]\n"
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "+
             "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
             f"Style: TikTok,{font_name},{font_size},{primary_ass},&H00FFFFFF,{outline_ass},{back_ass},0,0,0,0,100,100,0,0,1,{outline},{shadow},{alignment},100,100,{margin_v},0\n"
             "\n[Events]\n"
             "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
    return style


def srt_time_to_ass(t: str) -> str:
    # 00:00:01,234 -> 0:00:01.23 (centésimas)
    h, m, rest = t.split(':')
    s, ms = rest.split(',')
    ms_cs = int(round(int(ms)/10))  # centésimas
    return f"{int(h)}:{int(m):02d}:{int(s):02d}.{ms_cs:02d}"


def convert_srt_to_ass_events(srt_path: str) -> str:
    """Convierte bloques SRT a líneas Dialogue ASS sin estilo ni cabecera."""
    events = []
    with open(srt_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read().strip() + "\n\n"
    import re
    blocks = re.split(r"\n\s*\n", content)
    for block in blocks:
        lines = [l for l in block.strip().splitlines() if l.strip()]
        if len(lines) < 2:
            continue
        # Primera línea puede ser índice numérico
        if lines[0].isdigit():
            lines = lines[1:]
        if not lines:
            continue
        # Línea de tiempos
        time_line = lines[0]
        if '-->' not in time_line:
            continue
        start, end = [x.strip() for x in time_line.split('-->')]
        start_ass = srt_time_to_ass(start)
        end_ass = srt_time_to_ass(end)
        text_lines = lines[1:]
        # Unir, escapar caracteres ASS básicos { } \
        text = '\n'.join(text_lines)
        text = text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')
        # Opcional: dividir líneas largas para simular estilo TikTok (máx ~40 chars por línea)
        wrapped = []
        for paragraph in text.split('\n'):
            words = paragraph.split()
            line = []
            acc = 0
            for w in words:
                lw = len(w) + 1
                if acc + lw > 38 and line:
                    wrapped.append(' '.join(line))
                    line = [w]
                    acc = len(w) + 1
                else:
                    line.append(w)
                    acc += lw
            if line:
                wrapped.append(' '.join(line))
        final_text = '\\N'.join(wrapped) if wrapped else text
        events.append(f"Dialogue: 0,{start_ass},{end_ass},TikTok,,0,0,0,,{final_text}")
    return '\n'.join(events) + '\n'


def generate_temp_ass(srt_path: str, font_name: str, font_size: int, primary_color: str,
                      outline_color: str, outline: int, shadow: int, box: bool, box_color: str,
                      margin_v: int, alignment: int) -> str:
    header = build_ass_header(font_name, font_size, primary_color, outline_color, outline, shadow,
                              box, box_color, margin_v, alignment)
    events = convert_srt_to_ass_events(srt_path)
    return header + events


def build_ffmpeg_filters(args, input_video: str, ass_path: str) -> str:
    filters = []
    # Escalado / formateo vertical si se pide
    if args.tiktok_vertical:
        # target size
        tgt_w, tgt_h = args.target_size
        # Primero escalamos el video manteniendo ratio hasta cubrir alto, luego recortamos / rellenamos.
        # Usamos scale con force_original_aspect_ratio=decrease y luego pad si falta.
        filters.append(f"scale=w={tgt_w}:h={tgt_h}:force_original_aspect_ratio=decrease")
        filters.append(f"pad={tgt_w}:{tgt_h}:(ow-iw)/2:(oh-ih)/2:black")
    # Subtítulos ASS
    # Problema original: En Windows la ruta con ':' y espacios puede ser mal interpretada por el parser del filtro 'ass'
    # Solución: usar sintaxis filename= y escapar caracteres especiales según docs de ffmpeg (',' ':' '=' y "'")
    normalized = ass_path.replace('\\', '/')
    # Escapar caracteres especiales para ffmpeg filter args: ',' ':' '=' "'" '[' ']'
    esc_map = {',': '\\,', ':': '\\:', '=': '\\=', "'": "\\'", '[': '\\[', ']': '\\]'}
    escaped = ''.join(esc_map.get(c, c) for c in normalized)
    # Usamos sintaxis filename= para claridad
    filters.append(f"ass=filename='{escaped}'")
    return ','.join(filters)


def run_ffmpeg(input_video: str, output_video: str, filter_complex: str, vcodec: str, crf: int, preset: str, audio_copy: bool):
    cmd = [
        'ffmpeg', '-y',
        '-i', input_video,
        '-vf', filter_complex,
    ]
    if audio_copy:
        cmd += ['-c:a', 'copy']
    else:
        cmd += ['-c:a', 'aac', '-b:a', '192k']
    cmd += ['-c:v', vcodec, '-crf', str(crf), '-preset', preset, output_video]
    print('\nEjecutando:\n' + ' '.join(cmd) + '\n')
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando ffmpeg: {e}")
        sys.exit(1)


def parse_target_size(ts: str):
    try:
        w, h = ts.lower().split('x')
        return int(w), int(h)
    except Exception:
        raise argparse.ArgumentTypeError("Formato de tamaño inválido. Usa 1080x1920")


def main():
    parser = argparse.ArgumentParser(
        description="Quitar (hardcode) subtítulos .srt en un video con estilo TikTok usando ffmpeg + ASS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Ejemplos:\n  python burn_tiktok_subs.py input.mp4 subs.srt -o output.mp4\n  python burn_tiktok_subs.py input.mp4 subs.srt --tiktok-vertical\n  python burn_tiktok_subs.py input.mp4 subs.srt --font-size 72 --outline 4 --box --box-color 000000@0.4\n"""
    )
    parser.add_argument('video', help='Video de entrada')
    parser.add_argument('srt', help='Archivo .srt')
    parser.add_argument('-o', '--output', help='Video de salida (por defecto: *_tiktok.mp4)')
    parser.add_argument('--font-name', default='Arial', help='Fuente (default: Arial)')
    parser.add_argument('--font-size', type=int, default=68, help='Tamaño de fuente base (default: 68)')
    parser.add_argument('--color', default='FFFFFF', help='Color texto RGB hex (sin #) + opcional @alpha (0-1)')
    parser.add_argument('--outline-color', default='000000', help='Color borde')
    parser.add_argument('--outline', type=int, default=4, help='Grosor borde (outline)')
    parser.add_argument('--shadow', type=int, default=0, help='Sombra (shadow) en libass')
    parser.add_argument('--bottom-margin', type=int, default=160, help='Margen inferior en px (vertical)')
    parser.add_argument('--align', choices=['bottom','middle','top'], default='bottom', help='Alineación vertical')
    parser.add_argument('--box', action='store_true', help='Activar caja de fondo')
    parser.add_argument('--box-color', default='000000@0.55', help='Color caja/back (&HAABBGGRR) estilo simple RRGGBB@alpha')
    parser.add_argument('--tiktok-vertical', action='store_true', help='Forzar formato vertical 9:16')
    parser.add_argument('--target-size', type=parse_target_size, default='1080x1920', help='Resolución destino si vertical (default 1080x1920)')
    parser.add_argument('--vcodec', default='libx264', help='Codec de video (libx264, libx265, h264_nvenc, etc)')
    parser.add_argument('--crf', type=int, default=20, help='CRF calidad (x264/x265)')
    parser.add_argument('--preset', default='medium', help='Preset ffmpeg (ultrafast..slow)')
    parser.add_argument('--copy-audio', action='store_true', help='Copiar audio sin recomprimir')

    args = parser.parse_args()

    # Normalizar target_size si string (argparse lo convierte por parse_target_size)
    if isinstance(args.target_size, str):
        args.target_size = parse_target_size(args.target_size)

    # Validar archivos
    if not os.path.exists(args.video):
        print(f"❌ No existe video: {args.video}")
        sys.exit(1)
    if not os.path.exists(args.srt):
        print(f"❌ No existe SRT: {args.srt}")
        sys.exit(1)

    if not args.output:
        stem = str(Path(args.video).stem)
        args.output = f"{stem}_tiktok.mp4"

    alignment_map = {'bottom':2,'middle':5,'top':8}
    alignment = alignment_map[args.align]

    # Generar ASS temporal
    with tempfile.TemporaryDirectory() as tmpd:
        ass_path = os.path.join(tmpd, 'styled.ass')
        ass_text = generate_temp_ass(
            srt_path=args.srt,
            font_name=args.font_name,
            font_size=args.font_size,
            primary_color=args.color,
            outline_color=args.outline_color,
            outline=args.outline,
            shadow=args.shadow,
            box=args.box,
            box_color=args.box_color,
            margin_v=args.bottom_margin,
            alignment=alignment
        )
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_text)

        # Construir filtros ffmpeg
        filter_chain = build_ffmpeg_filters(args, args.video, ass_path)

        print("================ TikTok Subtitle Burner ================")
        print(f"Video: {args.video}")
        print(f"SRT:   {args.srt}")
        print(f"Salida: {args.output}")
        if args.tiktok_vertical:
            print(f"Formato vertical: {args.target_size[0]}x{args.target_size[1]}")
        print(f"Fuente: {args.font_name} {args.font_size}px Outline:{args.outline}")
        print(f"Caja: {'ON' if args.box else 'OFF'} Color:{args.box_color if args.box else '-'}")
        print("========================================================")

        run_ffmpeg(
            input_video=args.video,
            output_video=args.output,
            filter_complex=filter_chain,
            vcodec=args.vcodec,
            crf=args.crf,
            preset=args.preset,
            audio_copy=args.copy_audio
        )

    print(f"\n✅ Listo: {args.output}")


if __name__ == '__main__':
    main()
