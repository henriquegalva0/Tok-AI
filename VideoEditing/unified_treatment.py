#!/usr/bin/env python3
"""
Editor de Vídeo Unificado - Pipeline completo de edição
Combina sobreposição de vídeos, edição de áudio e aplicação de legendas
CORREÇÕES: Manter FPS original e sincronização precisa
"""

import cv2
import numpy as np
import os
import sys
import json
import re
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import VideoFileClip, CompositeAudioClip
import assemblyai as aai

class UnifiedVideoEditor:
    def __init__(self):
        self.temp_files = []
        # Removido target_fps - usar FPS original do vídeo
        
    def load_api_key(self):
        """Load AssemblyAI API key"""
        try:
            with open("VideoEditing/api_assembly.json", "r") as file:
                api_data = json.load(file)
                return api_data['api_key']
        except FileNotFoundError:
            api_key = os.getenv('ASSEMBLYAI_API_KEY')
            if not api_key:
                raise ValueError("API key not found. Please create api_assembly.json file or set ASSEMBLYAI_API_KEY environment variable")
            return api_key

    def srt_time_to_seconds(self, time_str):
        """Convert SRT time format to seconds"""
        time_str = time_str.replace(',', '.')
        time_obj = datetime.strptime(time_str, '%H:%M:%S.%f')
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1000000

    def parse_srt_content(self, srt_content):
        """Parse SRT content and return list of subtitle segments"""
        segments = []
        blocks = srt_content.strip().split('\n\n')
        
        for block in blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                time_line = lines[1]
                text_lines = lines[2:]
                
                time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
                if time_match:
                    start_time = self.srt_time_to_seconds(time_match.group(1))
                    end_time = self.srt_time_to_seconds(time_match.group(2))
                    text = ' '.join(text_lines)
                    
                    segments.append({
                        'start': start_time,
                        'end': end_time,
                        'text': text
                    })
        
        return segments

    def calculate_font_size(self, frame_width, frame_height):
        """Calculate appropriate font size based on frame dimensions"""
        # Tamanho da fonte baseado na resolução (mais conservador)
        base_size = min(frame_width, frame_height) // 25  # Reduzido de //20 para //25
        return max(20, min(base_size, 40))  # Entre 20 e 40 pixels

    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Palavra muito longa, força quebra
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def add_text_to_frame_pil(self, frame, text):
        """Add text to frame using PIL with adaptive font size and text wrapping"""
        height, width = frame.shape[:2]
        
        # Convert OpenCV frame to PIL Image
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(frame_rgb)
        draw = ImageDraw.Draw(pil_image)
        
        # Calculate appropriate font size
        font_size = self.calculate_font_size(width, height)
        
        # Try to load Comic Sans font with calculated size
        try:
            font_path = "C:/Windows/Fonts/comic.ttf"
            font = ImageFont.truetype(font_path, font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Maximum width for text (80% of screen width)
        max_text_width = int(width * 0.8)
        
        # Wrap text to fit screen
        text_lines = self.wrap_text(text, font, max_text_width)
        
        # Calculate total text height
        line_height = font_size + 5  # Small spacing between lines
        total_text_height = len(text_lines) * line_height
        
        # Position text 160 units above center
        start_y = (height // 2) - 160 - (total_text_height // 2)
        
        # Draw each line
        for i, line in enumerate(text_lines):
            # Get text dimensions for centering
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            
            # Center horizontally
            x = (width - text_width) // 2
            y = start_y + (i * line_height)
            
            # Draw outline (black) - smaller outline for better readability
            outline_width = 2
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=(0, 0, 0))
            
            # Draw main text (white)
            draw.text((x, y), line, font=font, fill=(255, 255, 255))
        
        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def generate_subtitles(self, video_path):
        """Generate subtitles using AssemblyAI"""
        print("🎤 Generating subtitles with AssemblyAI...")
        
        try:
            api_key = self.load_api_key()
            aai.settings.api_key = api_key
            
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(video_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                print(f"❌ Transcription failed: {transcript.error}")
                return []
            
            # Legendas com menos caracteres por linha para melhor legibilidade
            srt_content = transcript.export_subtitles_srt(chars_per_caption=30)
            
            # Save SRT file for reference
            with open("subtitles.srt", "w", encoding="utf-8") as f:
                f.write(srt_content)
            
            segments = self.parse_srt_content(srt_content)
            print(f"✅ Generated {len(segments)} subtitle segments")
            return segments
            
        except Exception as e:
            print(f"❌ Error generating subtitles: {e}")
            return []

    def process_complete_video(self, 
                             base_video="output.avi",
                             overlay_video="input.mp4", 
                             audio_source="input.mp4",
                             output_path="final_video_complete.mp4",
                             volume_factor=1.0,
                             fade_in_duration=0,
                             fade_out_duration=0):
        """
        Complete video processing pipeline:
        1. Overlay videos
        2. Apply processed audio
        3. Generate and apply subtitles
        CORREÇÕES: Manter FPS original e sincronização precisa
        """
        
        print("🎬 Starting Unified Video Processing Pipeline (SYNC FIXED VERSION)")
        print("=" * 60)
        
        # Verify input files
        for file_path in [base_video, overlay_video, audio_source]:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                return False
        
        # Step 1: Generate subtitles from audio source
        print("\n📝 STEP 1: Generating Subtitles")
        subtitle_segments = self.generate_subtitles(audio_source)
        
        # Step 2: Process video with overlay and subtitles
        print("\n🎥 STEP 2: Processing Video with Overlay and Subtitles")
        
        # Open video captures
        cap_base = cv2.VideoCapture(base_video)
        cap_overlay = cv2.VideoCapture(overlay_video)
        
        if not cap_base.isOpened() or not cap_overlay.isOpened():
            print("❌ Error opening video files")
            return False
        
        try:
            # Get video properties - CORREÇÃO: Usar FPS original
            base_width = int(cap_base.get(cv2.CAP_PROP_FRAME_WIDTH))
            base_height = int(cap_base.get(cv2.CAP_PROP_FRAME_HEIGHT))
            base_fps = cap_base.get(cv2.CAP_PROP_FPS)  # Manter FPS original
            base_frames = int(cap_base.get(cv2.CAP_PROP_FRAME_COUNT))
            overlay_frames = int(cap_overlay.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"📊 Base: {base_width}x{base_height} - {base_frames} frames")
            print(f"📊 Using Original FPS: {base_fps:.2f} (no conversion)")
            print(f"📊 Overlay: {overlay_frames} frames")
            
            # Overlay settings
            overlay_width = 480
            overlay_height = 270
            overlay_x = (base_width - overlay_width) // 2
            overlay_y = 0
            
            # Create temporary video with overlay and subtitles
            temp_video_path = "temp_processed_video.mp4"
            self.temp_files.append(temp_video_path)
            
            # CORREÇÃO: Usar FPS original do vídeo base
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(temp_video_path, fourcc, base_fps, (base_width, base_height))
            
            frame_count = 0
            max_frames = min(base_frames, overlay_frames)
            
            print(f"⚙️ Processing {max_frames} frames with original timing...")
            
            while frame_count < max_frames:
                ret_base, frame_base = cap_base.read()
                ret_overlay, frame_overlay = cap_overlay.read()
                
                if not ret_base or not ret_overlay:
                    break
                
                # Add overlay
                frame_overlay_resized = cv2.resize(frame_overlay, (overlay_width, overlay_height))
                
                if overlay_y + overlay_height <= base_height and overlay_x + overlay_width <= base_width:
                    frame_base[overlay_y:overlay_y + overlay_height, 
                          overlay_x:overlay_x + overlay_width] = frame_overlay_resized
                
                # Add border to overlay
                cv2.rectangle(frame_base, 
                            (overlay_x - 1, overlay_y - 1), 
                            (overlay_x + overlay_width + 1, overlay_y + overlay_height + 1), 
                            (255, 255, 255), 1)
                
                # Add subtitles - CORREÇÃO: Usar FPS original para timing preciso
                current_time = frame_count / base_fps
                current_subtitle = None
                
                for segment in subtitle_segments:
                    if segment['start'] <= current_time <= segment['end']:
                        current_subtitle = segment['text']
                        break
                
                if current_subtitle:
                    frame_base = self.add_text_to_frame_pil(frame_base, current_subtitle)
                
                out.write(frame_base)
                frame_count += 1
                
                # Progress indicator
                if frame_count % (int(base_fps) * 5) == 0:  # Every 5 seconds
                    progress = (frame_count / max_frames) * 100
                    print(f"⏳ Progress: {progress:.1f}%")
            
            cap_base.release()
            cap_overlay.release()
            out.release()
            cv2.destroyAllWindows()
            
            print(f"✅ Video processing completed: {frame_count} frames at {base_fps:.2f} FPS")
            
            # Step 3: Apply processed audio with precise sync
            print("\n🔊 STEP 3: Applying Processed Audio with Precise Sync")
            
            # CORREÇÃO: Carregar vídeos com duração exata
            temp_video_clip = VideoFileClip(temp_video_path)
            audio_source_clip = VideoFileClip(audio_source)
            
            # Get exact durations
            video_duration = temp_video_clip.duration
            audio_duration = audio_source_clip.audio.duration if audio_source_clip.audio else 0
            
            print(f"📏 Video duration: {video_duration:.3f}s")
            print(f"📏 Audio duration: {audio_duration:.3f}s")
            
            # Extract and process audio
            audio_to_apply = audio_source_clip.audio
            
            if audio_to_apply is None:
                print("⚠️ No audio found in source file")
                return False
            
            # CORREÇÃO: Ajustar áudio para duração exata do vídeo
            if abs(audio_duration - video_duration) > 0.1:  # Diferença > 100ms
                print(f"⚠️ Duration mismatch detected. Adjusting audio...")
                if audio_duration > video_duration:
                    audio_to_apply = audio_to_apply.subclip(0, video_duration)
                    print(f"🔧 Audio trimmed to {video_duration:.3f}s")
                else:
                    # Se áudio for mais curto, não estender (pode causar dessinc)
                    print(f"⚠️ Audio is shorter than video. Keeping original duration.")
            
            # Apply audio effects
            if volume_factor != 1.0:
                print(f"🔊 Adjusting volume to {volume_factor * 100}%")
                # audio_to_apply = audio_to_apply.set_volume(volume_factor)  # MoviePy method
                audio_to_apply = audio_to_apply.volumex(volume_factor)  # Alternative method
            
            if fade_in_duration > 0:
                print(f"📈 Applying fade in: {fade_in_duration}s")
                # audio_to_apply = audio_to_apply.fadein(fade_in_duration)  # MoviePy method
                audio_to_apply = audio_to_apply.audio_fadein(fade_in_duration)  # Alternative method
            
            if fade_out_duration > 0:
                print(f"📉 Applying fade out: {fade_out_duration}s")
                # audio_to_apply = audio_to_apply.fadeout(fade_out_duration)  # MoviePy method
                audio_to_apply = audio_to_apply.audio_fadeout(fade_out_duration)  # Alternative method
            
            # Apply audio to video
            final_video = temp_video_clip.set_audio(audio_to_apply)
            
            # CORREÇÃO: Export com configurações precisas para sync
            print(f"💾 Exporting final video: {output_path}")
            final_video.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                fps=base_fps,  # Usar FPS original
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None,
                # CORREÇÃO: Configurações adicionais para sync
                preset='medium',
                ffmpeg_params=['-avoid_negative_ts', 'make_zero']
            )
            
            # Cleanup
            temp_video_clip.close()
            audio_source_clip.close()
            final_video.close()
            
            print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"📁 Final video saved as: {output_path}")
            print(f"⏱️ Duration: {video_duration:.3f}s")
            print(f"🎬 FPS: {base_fps:.2f} (original)")
            print("🔧 SYNC FIXES APPLIED:")
            print("   ✅ Original FPS maintained")
            print("   ✅ Precise duration matching")
            print("   ✅ Text positioned 160px above center")
            print("   ✅ FFmpeg sync parameters added")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during processing: {e}")
            return False
        
        finally:
            # Cleanup temporary files
            self.cleanup_temp_files()

    def cleanup_temp_files(self):
        """Clean up temporary files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"🗑️ Cleaned up: {temp_file}")
            except Exception as e:
                print(f"⚠️ Could not remove {temp_file}: {e}")

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Unified Video Editor - Complete Pipeline (SYNC FIXED)')
    parser.add_argument('--base', default='output.avi', help='Base video file')
    parser.add_argument('--overlay', default='input.mp4', help='Overlay video file')
    parser.add_argument('--audio', default='input.mp4', help='Audio source file')
    parser.add_argument('--output', default='final_video_complete.mp4', help='Output file')
    parser.add_argument('--volume', type=float, default=1.0, help='Volume factor (1.0 = 100%)')
    parser.add_argument('--fade-in', type=float, default=0, help='Fade in duration (seconds)')
    parser.add_argument('--fade-out', type=float, default=0, help='Fade out duration (seconds)')
    
    args = parser.parse_args()
    
    editor = UnifiedVideoEditor()
    
    success = editor.process_complete_video(
        base_video=args.base,
        overlay_video=args.overlay,
        audio_source=args.audio,
        output_path=args.output,
        volume_factor=args.volume,
        fade_in_duration=args.fade_in,
        fade_out_duration=args.fade_out
    )
    
    if success:
        print("\n✅ All processing completed successfully!")
        try:
            os.remove("output.avi")
            os.remove("subtitles.srt")
        except FileNotFoundError:
            print(f"File not found.")
    else:
        print("\n❌ Processing failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
