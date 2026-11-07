from dotenv import load_dotenv

load_dotenv()

from config.logger import logger, set_request_id
from graph.graph import app

if __name__ == "__main__":
    set_request_id()
    question = "How to make pizza?"
    logger.info("Invoking graph", extra={"question": question})
    result = app.invoke(input={"question": question})
    logger.info("Graph finished", extra={"generation": result.get("generation")})
