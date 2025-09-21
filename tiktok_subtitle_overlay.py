#!/usr/bin/env python3
"""
TikTok Style Subtitle Overlay
============================

Componente para añadir subtítulos al estilo TikTok a videos.
Genera videos con subtítulos grandes, centrados y con efectos visuales.

Autor: Sistema de Transcripción de Gaming
Fecha: 2025
"""

import os
import re
import sys
import argparse
from datetime import timedelta
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass

try:
    from moviepy.editor import (
        VideoFileClip, 
        TextClip, 
        CompositeVideoClip,
        ColorClip,
        ImageClip
    )
    # Versiones diferentes de moviepy tienen diferentes ubicaciones
    try:
        from moviepy.config import check_presence_of_ffmpeg
    except ImportError:
        # En versiones más antiguas de moviepy
        def check_presence_of_ffmpeg():
            import os
            try:
                os.system('ffmpeg -version > nul 2>&1')
                return True
            except:
                return False
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    print(f"ERROR: moviepy no está disponible. Error: {e}")
    print("Instálalo con: pip install moviepy")
    print("O si estás en un entorno virtual, asegúrate de que esté activado.")
    # Crear clases dummy para evitar errores de definición
    class VideoFileClip: pass
    class TextClip: pass
    class CompositeVideoClip: pass
    class ColorClip: pass
    class ImageClip: pass
    def check_presence_of_ffmpeg(): pass
    MOVIEPY_AVAILABLE = False


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


class TikTokSubtitleGenerator:
    """Generador de videos con subtítulos al estilo TikTok"""
    
    def __init__(self, 
                 font_size: int = 60,
                 font_color: str = 'white',
                 stroke_color: str = 'black',
                 stroke_width: int = 3,
                 font_family: str = 'Arial-Bold',
                 background_opacity: float = 0.7):
        """
        Inicializa el generador con configuración de estilo.
        
        Args:
            font_size: Tamaño de la fuente
            font_color: Color del texto
            stroke_color: Color del contorno
            stroke_width: Grosor del contorno
            font_family: Familia de fuente
            background_opacity: Opacidad del fondo semi-transparente
        """
        self.font_size = font_size
        self.font_color = font_color
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.font_family = font_family
        self.background_opacity = background_opacity
        
        # Verificar que FFmpeg esté disponible
        try:
            check_presence_of_ffmpeg()
        except Exception as e:
            print(f"ERROR: FFmpeg no está disponible: {e}")
            sys.exit(1)
    
    def create_subtitle_clip(self, 
                           subtitle: Subtitle, 
                           video_size: Tuple[int, int]) -> CompositeVideoClip:
        """
        Crea un clip de texto para un subtítulo al estilo TikTok usando PIL.
        
        Args:
            subtitle: Objeto Subtitle con el texto y timing
            video_size: Tupla (ancho, alto) del video
            
        Returns:
            CompositeVideoClip configurado con el estilo TikTok
        """
        # Dividir texto largo en múltiples líneas
        words = subtitle.text.split()
        max_words_per_line = 6  # Máximo palabras por línea para TikTok
        
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(current_line) >= max_words_per_line:
                lines.append(' '.join(current_line))
                current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        text = '\n'.join(lines)
        
        # Usar un método alternativo sin ImageMagick
        try:
            from PIL import Image, ImageDraw, ImageFont
            import tempfile
            import os
            
            # Crear imagen con PIL
            width, height = video_size[0], int(video_size[1] * 0.3)  # 30% inferior del video
            img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Intentar cargar fuente, usar default si falla
            try:
                font = ImageFont.truetype("arial.ttf", self.font_size)
            except:
                try:
                    font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", self.font_size)
                except:
                    font = ImageFont.load_default()
            
            # Calcular posición del texto (centrado)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = height - text_height - 20  # 20px desde el bottom
            
            # Dibujar contorno (stroke)
            stroke_width = self.stroke_width
            stroke_color = self.stroke_color
            if stroke_color == 'black':
                stroke_color = (0, 0, 0, 255)
            elif stroke_color == 'white':
                stroke_color = (255, 255, 255, 255)
            
            # Dibujar el contorno
            for dx in range(-stroke_width, stroke_width + 1):
                for dy in range(-stroke_width, stroke_width + 1):
                    if dx*dx + dy*dy <= stroke_width*stroke_width:
                        draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
            
            # Dibujar texto principal
            text_color = self.font_color
            if text_color == 'white':
                text_color = (255, 255, 255, 255)
            elif text_color == 'yellow':
                text_color = (255, 255, 0, 255)
            elif text_color == 'black':
                text_color = (0, 0, 0, 255)
            else:
                # Intentar parsear color hex
                try:
                    if text_color.startswith('#'):
                        hex_color = text_color[1:]
                        text_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
                    else:
                        text_color = (255, 255, 255, 255)  # Default a blanco
                except:
                    text_color = (255, 255, 255, 255)
            
            draw.text((x, y), text, font=font, fill=text_color)
            
            # Guardar imagen temporal
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                img.save(tmp_file.name)
                tmp_path = tmp_file.name
            
            # Crear ImageClip en lugar de TextClip
            from moviepy.editor import ImageClip
            txt_clip = ImageClip(tmp_path, duration=subtitle.end_time - subtitle.start_time)
            txt_clip = txt_clip.set_start(subtitle.start_time)
            
            # Posicionar en la parte inferior del video (estilo TikTok)
            txt_clip = txt_clip.set_position(('center', 'bottom'))
            
            # Limpiar archivo temporal
            try:
                os.unlink(tmp_path)
            except:
                pass
            
            return txt_clip
            
        except ImportError:
            # Fallback: usar TextClip simple si PIL no está disponible
            print("ADVERTENCIA: PIL no disponible, usando TextClip básico")
            txt_clip = TextClip(
                text,
                fontsize=self.font_size,
                color=self.font_color,
                font='Arial',  # Fuente básica
                method='label'
            ).set_start(subtitle.start_time).set_duration(subtitle.end_time - subtitle.start_time)
            
            txt_clip = txt_clip.set_position(('center', 'bottom'))
            return txt_clip
    
    def create_background_clip(self, 
                             subtitle: Subtitle, 
                             txt_clip,  # Puede ser TextClip o ImageClip
                             video_size: Tuple[int, int]) -> Optional[ColorClip]:
        """
        Crea un fondo semi-transparente para el texto.
        
        Args:
            subtitle: Objeto Subtitle
            txt_clip: Clip de texto correspondiente
            video_size: Tamaño del video
            
        Returns:
            ColorClip con fondo semi-transparente o None
        """
        if self.background_opacity <= 0:
            return None
        
        # Obtener el tamaño del texto
        try:
            txt_size = txt_clip.size
            if txt_size[0] is None or txt_size[1] is None:
                return None
        except:
            # Si no podemos obtener el tamaño, usar un tamaño por defecto
            txt_size = (video_size[0] * 0.8, 100)
        
        # Crear fondo negro semi-transparente
        bg_clip = ColorClip(
            size=(txt_size[0] + 20, txt_size[1] + 10),  # Padding
            color=(0, 0, 0),
            duration=subtitle.end_time - subtitle.start_time
        ).set_opacity(self.background_opacity).set_start(subtitle.start_time)
        
        # Posicionar el fondo en la misma ubicación que el texto
        bg_clip = bg_clip.set_position(('center', 'bottom'))
        
        return bg_clip
    
    def generate_video_with_subtitles(self, 
                                    video_path: str, 
                                    srt_path: str, 
                                    output_path: str,
                                    progress_callback=None) -> bool:
        """
        Genera un video con subtítulos al estilo TikTok.
        
        Args:
            video_path: Ruta al video de entrada
            srt_path: Ruta al archivo de subtítulos .srt
            output_path: Ruta de salida para el video generado
            progress_callback: Función callback para mostrar progreso
            
        Returns:
            True si la generación fue exitosa, False en caso contrario
        """
        try:
            print(f"Cargando video: {video_path}")
            video = VideoFileClip(video_path)
            video_size = video.size
            
            print(f"Parseando subtítulos: {srt_path}")
            subtitles = SRTParser.parse_srt_file(srt_path)
            print(f"Encontrados {len(subtitles)} subtítulos")
            
            if not subtitles:
                print("ADVERTENCIA: No se encontraron subtítulos válidos")
                return False
            
            # Crear clips de subtítulos
            subtitle_clips = []
            background_clips = []
            
            print("Generando clips de subtítulos...")
            for i, subtitle in enumerate(subtitles):
                if progress_callback:
                    progress_callback(i, len(subtitles), f"Procesando subtítulo {i+1}")
                
                # Verificar que el subtítulo esté dentro de la duración del video
                if subtitle.start_time >= video.duration:
                    continue
                
                # Ajustar el tiempo final si excede la duración del video
                end_time = min(subtitle.end_time, video.duration)
                subtitle.end_time = end_time
                
                # Crear clip de texto
                txt_clip = self.create_subtitle_clip(subtitle, video_size)
                subtitle_clips.append(txt_clip)
                
                # Crear fondo si está habilitado
                bg_clip = self.create_background_clip(subtitle, txt_clip, video_size)
                if bg_clip:
                    background_clips.append(bg_clip)
            
            print(f"Componiendo video final con {len(subtitle_clips)} subtítulos...")
            
            # Componer video final
            all_clips = [video] + background_clips + subtitle_clips
            final_video = CompositeVideoClip(all_clips)
            
            print(f"Exportando video a: {output_path}")
            
            # Configuración de exportación optimizada
            final_video.write_videofile(
                output_path,
                fps=video.fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Limpiar recursos
            video.close()
            final_video.close()
            for clip in subtitle_clips + background_clips:
                clip.close()
            
            print(f"✅ Video generado exitosamente: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error generando video: {str(e)}")
            return False


def progress_callback(current: int, total: int, message: str):
    """Callback para mostrar progreso."""
    percentage = (current / total) * 100
    print(f"Progreso: {percentage:.1f}% - {message}")


def main():
    """Función principal del script."""
    # Verificar moviepy al inicio
    if not MOVIEPY_AVAILABLE:
        print("\n❌ No se puede continuar sin moviepy.")
        print("Verifica que moviepy esté instalado en tu entorno actual:")
        print(f"  python -c \"import moviepy; print('MoviePy versión:', moviepy.__version__)\"")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Genera videos con subtítulos al estilo TikTok",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt -o video_con_subs.mp4
  python tiktok_subtitle_overlay.py video.mp4 subtitulos.srt --font-size 80 --stroke-width 4
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
    parser.add_argument('--stroke-color', default='black',
                       help='Color del contorno (por defecto: black)')
    parser.add_argument('--stroke-width', type=int, default=3,
                       help='Grosor del contorno (por defecto: 3)')
    parser.add_argument('--font-family', default='Arial-Bold',
                       help='Familia de fuente (por defecto: Arial-Bold)')
    parser.add_argument('--background-opacity', type=float, default=0.0,
                       help='Opacidad del fondo (0.0-1.0, por defecto: 0.0)')
    
    args = parser.parse_args()
    
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
        args.output = f"{video_name}_con_subtitulos{video_ext}"
    
    # Crear directorio de salida si no existe
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("🎬 Generador de Subtítulos TikTok")
    print("=" * 40)
    print(f"Video de entrada: {args.video}")
    print(f"Subtítulos: {args.srt}")
    print(f"Video de salida: {args.output}")
    print(f"Configuración: Fuente {args.font_size}px, Color {args.font_color}")
    print("=" * 40)
    
    # Crear generador
    generator = TikTokSubtitleGenerator(
        font_size=args.font_size,
        font_color=args.font_color,
        stroke_color=args.stroke_color,
        stroke_width=args.stroke_width,
        font_family=args.font_family,
        background_opacity=args.background_opacity
    )
    
    # Generar video
    success = generator.generate_video_with_subtitles(
        args.video,
        args.srt,
        args.output,
        progress_callback=progress_callback
    )
    
    if success:
        print(f"\n🎉 ¡Video generado exitosamente!")
        print(f"📁 Archivo: {args.output}")
        sys.exit(0)
    else:
        print(f"\n❌ Error generando el video.")
        sys.exit(1)


if __name__ == "__main__":
    main()