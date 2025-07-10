from moviepy.editor import VideoFileClip, AudioFileClip
import os

def merge_video_with_audio(video_path, audio_path, output_path):
    """
    Mescla um arquivo de vídeo com um arquivo de áudio,
    ajustando a duração do áudio para corresponder ao vídeo.
    
    Args:
        video_path (str): Caminho para o arquivo de vídeo
        audio_path (str): Caminho para o arquivo de áudio
        output_path (str): Caminho para o arquivo de saída
    """
    
    try:
        # Carrega o vídeo
        print("Carregando vídeo...")
        video = VideoFileClip(video_path)
        video_duration = video.duration
        print(f"Duração do vídeo: {video_duration:.2f} segundos")
        
        # Carrega o áudio
        print("Carregando áudio...")
        audio = AudioFileClip(audio_path)
        audio_duration = audio.duration
        print(f"Duração do áudio original: {audio_duration:.2f} segundos")
        
        # Ajusta o áudio para a duração do vídeo
        if audio_duration > video_duration:
            # Se o áudio é mais longo, corta para a duração do vídeo
            print("Cortando áudio para corresponder à duração do vídeo...")
            adjusted_audio = audio.subclip(0, video_duration)
        elif audio_duration < video_duration:
            # Se o áudio é mais curto, repete até preencher a duração do vídeo
            print("Repetindo áudio para corresponder à duração do vídeo...")
            loops_needed = int(video_duration / audio_duration) + 1
            repeated_audio = audio
            for _ in range(loops_needed - 1):
                repeated_audio = repeated_audio.concatenate_audioclip(audio)
            adjusted_audio = repeated_audio.subclip(0, video_duration)
        else:
            # Se as durações são iguais, usa o áudio original
            print("Durações são iguais, usando áudio original...")
            adjusted_audio = audio
        
        # Remove o áudio original do vídeo (se houver) e adiciona o novo áudio
        print("Mesclando vídeo com áudio...")
        final_video = video.set_audio(adjusted_audio)
        
        # Salva o resultado
        print(f"Salvando vídeo final em: {output_path}")
        final_video.write_videofile(
            output_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            verbose=False,
            logger=None
        )
        
        # Libera recursos
        video.close()
        audio.close()
        adjusted_audio.close()
        final_video.close()
        
        print("✅ Vídeo final criado com sucesso!")
        print(f"Arquivo salvo: {output_path}")
        try:
            os.remove("output.avi")
            os.remove("subtitles.srt")
        except FileNotFoundError:
            print(f"File not found.")
        
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo não encontrado - {e}")
    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")

def main():
    # Caminhos dos arquivos
    video_path = "output.avi"
    audio_path = "MusicsColiseum/musica_aleatoria.mp3"
    output_path = "video_final.mp4"
    
    # Verifica se os arquivos existem
    if not os.path.exists(video_path):
        print(f"❌ Erro: Arquivo de vídeo não encontrado: {video_path}")
        return
    
    if not os.path.exists(audio_path):
        print(f"❌ Erro: Arquivo de áudio não encontrado: {audio_path}")
        return
    
    # Executa a mesclagem
    merge_video_with_audio(video_path, audio_path, output_path)

if __name__ == "__main__":
    main()
