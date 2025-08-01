import json
import os
import zipfile

class CodeGenerationAgent:
    def __init__(self, llm_reasoner, github_manager):
        self.llm = llm_reasoner
        self.github = github_manager

    def generate_codebase(self, architecture_file, specifications_file):
        # Read system architecture and specifications from GitHub
        architecture = self.github.read_file(architecture_file)
        specifications = self.github.read_file(specifications_file)

        # Generate codebase
        prompt = (
            f"You are a software engineer. Based on the following system architecture and specifications, "
            f"generate all required Python-Files. Respond in JSON format with this structure:.\n\n"
            f"{{\n"
            f"  \"files\": [\n"
            f"    {{\n"
            f"      \"filename\": \"<filename>\",\n"
            f"      \"content\": \"<file-content>\"\n"
            f"    }},\n"
            f"    ...\n"
            f"  ]\n"
            f"}}\n\n"
            f"System Architecture:\n{architecture}\n\n"
            f"System Specifications:\n{specifications}"
        )

        #codebase = self.llm.get_chat_response(prompt)
        codebase = self.llm.get_chat_response(
            prompt#,
            #response_format={ "type": "json_object" }
        ) # Get the response in JSON format

        print(codebase)

        # Save codebase
        txt_path = 'outputs/generated_codebase.txt'

        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(codebase)

        file_path = 'outputs/generated_codebase.zip'

        codebase = save_codebase_as_zip(txt_path, file_path)

        commit_message = "Generated Codebase"
        
        try:
            # Check if the file exists
            existing_file = self.github.get_contents(file_path)
            self.github.update_file(file_path, commit_message, codebase, existing_file.sha)
        except self.github.GithubException as e:
            if e.status == 404:
                # File does not exist, create it
                self.github.create_file(file_path, commit_message, codebase)
            else:
                raise e

        return codebase


def save_codebase_as_zip(codebase_json_path, zip_path):
    # Lade das JSON aus der Datei
    with open(codebase_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    #print(data)

    # Liste der Dateien aus dem JSON auslesen
    files = data.get("files", [])

    # ZIP-Datei erstellen
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Durch alle Einträge im JSON iterieren
        # Hier ist jeder Schlüssel ein Dateiname und jeder Wert der Dateiinhalt
        for file_info in files:
            filename = file_info.get("filename")
            content = file_info.get("content")
            if isinstance(content, list):
                content = "\n".join(content)
            zipf.writestr(filename, content)

    # ZIP-Datei als Bytes zurückgeben
    with open(zip_path, 'rb') as f:
        return f.read()