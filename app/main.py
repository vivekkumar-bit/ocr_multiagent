import app.utils.config  # This triggers load_dotenv()
from app.graph.workflow import build_graph

graph = build_graph()

def run_pipeline(file_bytes, file_type):
    return graph.invoke({
        "file_bytes": file_bytes,
        "file_type": file_type
    })
