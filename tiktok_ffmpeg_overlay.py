#!/usr/bin/env python3
"""
TikTok Style Subtitle Overlay usando FFmpeg
==========================================

Componente para añadir subtítulos al estilo TikTok a videos usando FFmpeg.
Evita dependencias problemáticas como ImageMagick.

Autor: Sistema de Transcripción de Gaming
Fecha: 2025
"""

import os
import re
import sys
import argparse
import subprocess
from datetime import timedelta
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class Subtitle:
    """Clase para representar un subtítulo con timestamps."""
    start_time: float  # En segundos
    end_time: float    # En segundos
    text: str
    index: int


class SRTParser:
    """Parser para archivos de subtítulos .srt"""
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> float:
        """
        Convierte timestamp SRT (HH:MM:SS,mmm) a segundos.
        
        Args:
            timestamp_str: Timestamp en formato SRT
            
        Returns:
            Tiempo en segundos como float
        """
        # Formato: HH:MM:SS,mmm
        time_part, ms_part = timestamp_str.split(',')
        hours, minutes, seconds = map(int, time_part.split(':'))
        milliseconds = int(ms_part)
        
        total_seconds = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000
        return total_seconds
    
    @staticmethod
    def parse_srt_file(srt_path: str) -> List[Subtitle]:
        """
        Parsea un archivo .srt y devuelve una lista de subtítulos.
        
        Args:
            srt_path: Ruta al archivo .srt
            
        Returns:
            Lista de objetos Subtitle
        """
        if not os.path.exists(srt_path):
            raise FileNotFoundError(f"Archivo SRT no encontrado: {srt_path}")
        
        subtitles = []
        
        with open(srt_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        
        # Dividir en bloques de subtítulos
        subtitle_blocks = re.split(r'\n\s*\n', content)
        
        for block in subtitle_blocks:
            lines = block.strip().split('\n')
            if len(lines) < 3:
                continue
            
            try:
                # Línea 1: Índice
                index = int(lines[0])
                
                # Línea 2: Timestamps
                timestamp_line = lines[1]
                start_str, end_str = timestamp_line.split(' --> ')
                start_time = SRTParser.parse_timestamp(start_str.strip())
                end_time = SRTParser.parse_timestamp(end_str.strip())
                
                # Líneas 3+: Texto del subtítulo
                text = '\n'.join(lines[2:]).strip()
                
                subtitles.append(Subtitle(
                    start_time=start_time,
                    end_time=end_time,
                    text=text,
                    index=index
                ))
                
            except (ValueError, IndexError) as e:
                print(f"Advertencia: Error parseando subtítulo en bloque: {block[:50]}...")
                continue
        
        return subtitles


class FFmpegTikTokGenerator:
    """Generador de videos con subtítulos al estilo TikTok usando FFmpeg"""
    
    def __init__(self, 
                 font_size: int = 60,
                 font_color: str = 'white',
                 outline_color: str = 'black',
                 outline_width: int = 3,
                 tiktok_format: bool = False,
                 custom_resolution: Optional[Tuple[int, int]] = None):
        """
        Inicializa el generador con configuración de estilo.
        
        Args:
            font_size: Tamaño de la fuente
            font_color: Color del texto
            outline_color: Color del contorno  
            outline_width: Grosor del contorno
            tiktok_format: Si True, convierte a formato TikTok (9:16, 1080x1920)
            custom_resolution: Tupla (ancho, alto) para resolución personalizada
        """
        self.font_size = font_size
        self.font_color = font_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.tiktok_format = tiktok_format
        self.custom_resolution = custom_resolution
        
        # Verificar que FFmpeg esté disponible
        try:
            subprocess.run(['ffmpeg', '-version'], 
                         capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("ERROR: FFmpeg no está disponible o instalado")
            sys.exit(1)
    
    def create_ass_subtitles(self, subtitles: List[Subtitle], output_path: str) -> str:
        """
        Crea un archivo ASS con los subtítulos estilizados.
        
        Args:
            subtitles: Lista de subtítulos
            output_path: Ruta base para el archivo ASS
            
        Returns:
            Ruta al archivo ASS generado
        """
        ass_path = output_path.replace('.mp4', '.ass')
        
        # Plantilla ASS con estilo TikTok
        ass_content = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: TikTok,Arial,{self.font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,{self.outline_width},2,2,10,10,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        for subtitle in subtitles:
            # Convertir tiempo a formato ASS (H:MM:SS.CC)
            start_h, start_m, start_s = self._seconds_to_hms(subtitle.start_time)
            end_h, end_m, end_s = self._seconds_to_hms(subtitle.end_time)
            
            start_ass = f"{start_h}:{start_m:02d}:{start_s:05.2f}"
            end_ass = f"{end_h}:{end_m:02d}:{end_s:05.2f}"
            
            # Limpiar texto para ASS
            text = subtitle.text.replace('\n', '\\N')
            text = text.replace('"', '\\"')
            
            # Dividir en líneas si es muy largo
            words = text.split()
            if len(words) > 6:
                mid = len(words) // 2
                text = ' '.join(words[:mid]) + '\\N' + ' '.join(words[mid:])
            
            ass_content += f"Dialogue: 0,{start_ass},{end_ass},TikTok,,0,0,0,,{text}\n"
        
        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)
        
        return ass_path
    
    def _seconds_to_hms(self, seconds: float) -> Tuple[int, int, float]:
        """Convierte segundos a horas, minutos, segundos."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return hours, minutes, secs
    
    def get_video_resolution(self, video_path: str) -> Tuple[int, int]:
        """Obtiene la resolución del video."""
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            import json
            data = json.loads(result.stdout)
            
            for stream in data['streams']:
                if stream['codec_type'] == 'video':
                    return int(stream['width']), int(stream['height'])
        except:
            pass
        
        # Fallback
        return 1920, 1080
    
    def generate_video_with_subtitles(self, 
                                    video_path: str, 
                                    srt_path: str, 
                                    output_path: str,
                                    crop_mode: str = 'center') -> bool:
        """
        Genera un video con subtítulos al estilo TikTok usando FFmpeg.
        
        Args:
            video_path: Ruta al video de entrada
            srt_path: Ruta al archivo de subtítulos .srt
            output_path: Ruta de salida para el video generado
            crop_mode: Modo de recorte ('center', 'top', 'bottom')
            
        Returns:
            True si la generación fue exitosa, False en caso contrario
        """
        try:
            print(f"Cargando video: {video_path}")
            original_w, original_h = self.get_video_resolution(video_path)
            
            print(f"Parseando subtítulos: {srt_path}")
            subtitles = SRTParser.parse_srt_file(srt_path)
            print(f"Encontrados {len(subtitles)} subtítulos")
            
            if not subtitles:
                print("ADVERTENCIA: No se encontraron subtítulos válidos")
                return False
            
            # Crear archivo ASS
            print("Generando archivo de subtítulos ASS...")
            ass_path = self.create_ass_subtitles(subtitles, output_path)
            
            # Construir comando FFmpeg
            cmd = ['ffmpeg', '-i', video_path]
            
            # Filtros de video
            video_filters = []
            
            # Redimensionamiento para TikTok o resolución personalizada
            if self.tiktok_format or self.custom_resolution:
                if self.custom_resolution:
                    target_w, target_h = self.custom_resolution
                    print(f"Redimensionando a resolución personalizada: {target_w}x{target_h}")
                else:
                    target_w, target_h = 1080, 1920
                    print(f"Convirtiendo a formato TikTok: {target_w}x{target_h}")
                
                # Calcular recorte y escala
                original_ratio = original_w / original_h
                target_ratio = target_w / target_h
                
                if original_ratio > target_ratio:
                    # Video más ancho - recortar lados
                    new_h = original_h
                    new_w = int(original_h * target_ratio)
                    x_offset = (original_w - new_w) // 2
                    
                    video_filters.append(f"crop={new_w}:{new_h}:{x_offset}:0")
                else:
                    # Video más alto - recortar arriba/abajo según modo
                    new_w = original_w
                    new_h = int(original_w / target_ratio)
                    
                    if crop_mode == 'top':
                        y_offset = 0
                    elif crop_mode == 'bottom':
                        y_offset = original_h - new_h
                    else:  # center
                        y_offset = (original_h - new_h) // 2
                    
                    video_filters.append(f"crop={new_w}:{new_h}:0:{y_offset}")
                
                # Escalar al tamaño final
                video_filters.append(f"scale={target_w}:{target_h}")
            
            # Añadir subtítulos
            video_filters.append(f"ass={ass_path}")
            
            # Aplicar filtros
            if video_filters:
                cmd.extend(['-vf', ','.join(video_filters)])
            
            # Configuración de salida
            cmd.extend([
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'medium',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-y',  # Sobrescribir archivo existente
                output_path
            ])
            
            print(f"Ejecutando FFmpeg...")
            print(f"Comando: {' '.join(cmd[:10])}...")  # Mostrar solo parte del comando
            
            # Ejecutar FFmpeg
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0:
                print(f"✅ Video generado exitosamente: {output_path}")
                
                # Limpiar archivo ASS temporal
                try:
                    os.remove(ass_path)
                except:
                    pass
                
                return True
            else:
                print(f"❌ Error en FFmpeg:")
                print(process.stderr)
                return False
                
        except Exception as e:
            print(f"❌ Error generando video: {str(e)}")
            return False


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Genera videos con subtítulos al estilo TikTok usando FFmpeg",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python tiktok_ffmpeg_overlay.py video.mp4 subtitulos.srt -o video_con_subs.mp4
  python tiktok_ffmpeg_overlay.py video.mp4 subtitulos.srt --tiktok
  python tiktok_ffmpeg_overlay.py video.mp4 subtitulos.srt --resolution 720x1280
        """
    )
    
    parser.add_argument('video', help='Ruta al video de entrada')
    parser.add_argument('srt', help='Ruta al archivo de subtítulos .srt')
    parser.add_argument('-o', '--output', 
                       help='Ruta de salida (por defecto: {video}_con_subtitulos.mp4)')
    parser.add_argument('--font-size', type=int, default=60,
                       help='Tamaño de fuente (por defecto: 60)')
    parser.add_argument('--font-color', default='white',
                       help='Color del texto (por defecto: white)')
    parser.add_argument('--outline-color', default='black',
                       help='Color del contorno (por defecto: black)')
    parser.add_argument('--outline-width', type=int, default=3,
                       help='Grosor del contorno (por defecto: 3)')
    parser.add_argument('--tiktok', action='store_true',
                       help='Convertir a formato TikTok (9:16, 1080x1920)')
    parser.add_argument('--resolution', 
                       help='Resolución personalizada (ej: 720x1280)')
    parser.add_argument('--crop-mode', choices=['center', 'top', 'bottom'], default='center',
                       help='Modo de recorte cuando se cambia aspect ratio (por defecto: center)')
    
    args = parser.parse_args()
    
    # Procesar resolución personalizada
    custom_resolution = None
    if args.resolution:
        try:
            width, height = map(int, args.resolution.split('x'))
            custom_resolution = (width, height)
        except ValueError:
            print(f"❌ Error: Formato de resolución inválido. Usa formato 'ancho x alto' (ej: 720x1280)")
            sys.exit(1)
    
    # Validar argumentos
    if args.tiktok and custom_resolution:
        print("❌ Error: No puedes usar --tiktok y --resolution al mismo tiempo")
        sys.exit(1)
    
    # Validar archivos de entrada
    if not os.path.exists(args.video):
        print(f"❌ Error: Video no encontrado: {args.video}")
        sys.exit(1)
    
    if not os.path.exists(args.srt):
        print(f"❌ Error: Archivo SRT no encontrado: {args.srt}")
        sys.exit(1)
    
    # Generar nombre de salida si no se especifica
    if not args.output:
        video_name, video_ext = os.path.splitext(args.video)
        if args.tiktok:
            args.output = f"{video_name}_tiktok{video_ext}"
        else:
            args.output = f"{video_name}_con_subtitulos{video_ext}"
    
    # Crear directorio de salida si no existe
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("🎬 Generador de Subtítulos TikTok (FFmpeg)")
    print("=" * 40)
    print(f"Video de entrada: {args.video}")
    print(f"Subtítulos: {args.srt}")
    print(f"Video de salida: {args.output}")
    print(f"Configuración: Fuente {args.font_size}px, Color {args.font_color}")
    if args.tiktok:
        print("🎯 Formato: TikTok (9:16, 1080x1920)")
    elif custom_resolution:
        print(f"🎯 Resolución personalizada: {custom_resolution[0]}x{custom_resolution[1]}")
    print("=" * 40)
    
    # Crear generador
    generator = FFmpegTikTokGenerator(
        font_size=args.font_size,
        font_color=args.font_color,
        outline_color=args.outline_color,
        outline_width=args.outline_width,
        tiktok_format=args.tiktok,
        custom_resolution=custom_resolution
    )
    
    # Generar video
    success = generator.generate_video_with_subtitles(
        args.video,
        args.srt,
        args.output,
        crop_mode=args.crop_mode
    )
    
    if success:
        print(f"\n🎉 ¡Video generado exitosamente!")
        print(f"📁 Archivo: {args.output}")
        if args.tiktok:
            print("📱 Formato TikTok Ready (9:16)")
        sys.exit(0)
    else:
        print(f"\n❌ Error generando el video.")
        sys.exit(1)


if __name__ == "__main__":
    main()