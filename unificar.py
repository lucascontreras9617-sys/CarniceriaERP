import os

# Configuración: archivos o carpetas a ignorar
IGNORE_LIST = {
    '.git', 'node_modules', '__pycache__', '.venv', 'dist', 'out', 
    'target', 'bin', 'obj', 'vendor', '.idea', '.vscode', 'assets',
    'public', 'tests', 'migrations' # Los tests y migraciones pesan mucho y no definen la arquitectura
}
EXTENSIONS = {'.py', '.js', '.ts', '.java', '.cs', '.md'} # Ajusta según tu proyecto

def unificar_proyecto(output_file='contexto_proyecto.md'):
    with open(output_file, 'w', encoding='utf-8') as f_out:
        for root, dirs, files in os.walk('.'):
            # Filtrar carpetas ignoradas
            dirs[:] = [d for d in dirs if d not in IGNORE_LIST]
            
            for file in files:
                if any(file.endswith(ext) for ext in EXTENSIONS):
                    full_path = os.path.join(root, file)
                    f_out.write(f"\n\n--- FILE: {full_path} ---\n")
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f_in:
                            f_out.write(f_in.read())
                    except Exception as e:
                        f_out.write(f"[Error leyendo archivo: {e}]")

if __name__ == "__main__":
    unificar_proyecto()
    print("¡Proyecto unificado en contexto_proyecto.md!")