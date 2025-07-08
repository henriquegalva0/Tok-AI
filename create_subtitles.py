import assemblyai as aai
import json

with open("api_assembly.json", "r") as file:
    api_key = json.load(file)

def dictionary_treatment(subtitles_srt):
    subtitles_list = subtitles_srt.split("\n")

    dicionario = {}
    for i in range(0, len(subtitles_list), 4):
        if i + 2 < len(subtitles_list):
            chave = subtitles_list[i + 1]
            valor = subtitles_list[i + 2]
            dicionario[chave] = valor
    return dicionario

def time_treatment(dict_subtitles):
    novos_subtitulos = {}
    for key, value in dict_subtitles.items():
        time_start, time_end = key.split(" --> ")
        time_start = time_start.split(",")[0]
        time_end = time_end.split(",")[0]
        nova_chave = (time_start, time_end)
        novos_subtitulos[nova_chave] = value
    return novos_subtitulos

aai.settings.api_key = f"{api_key['api_key']}"

transcriber = aai.Transcriber().transcribe("clipe_family_guy.mp4")

subtitles = transcriber.export_subtitles_srt(chars_per_caption=20)

print("Legenda criada com sucesso!")

subtitles_dict = dictionary_treatment(subtitles)
subtitles_dict = time_treatment(subtitles_dict)

print(subtitles_dict)