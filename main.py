import platform
import shutil
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from llm import config
from llm.logger import logger


def create_api(app):
    from llm.api.api import Api

    api = Api(app)

    return api


@asynccontextmanager
async def lifespan(app: FastAPI):
    from llm.provider_manager import provider_manager

    await provider_manager.start_all()
    try:
        yield
    finally:
        # Teardown logic here (after yield)
        # If you have any teardown process, place it here. For example:
        # await close_db_connection()
        pass


XVFB_DISPLAY = None


def start_xvfb_display():
    global XVFB_DISPLAY
    if XVFB_DISPLAY is None:
        from xvfbwrapper import Xvfb

        XVFB_DISPLAY = Xvfb(width=config.SCREEN_WIDTH, height=config.SCREEN_HEIGHT)
        XVFB_DISPLAY.start()


# def clear_browser_data_folder():
    folder_path = "./browser_data"
    if os.path.exists(folder_path):
        logger.info(f"Clearing browser data folder: {folder_path}")
        shutil.rmtree(folder_path)
        os.makedirs(folder_path)
    else:
        logger.warning(f"Browser data folder does not exist: {folder_path}")


def api():
    from llm.shared_cmd_options import cmd_opts

    # 清空指定文件夹
    # clear_browser_data_folder()

    app = FastAPI(lifespan=lifespan)
    api = create_api(app)

    if config.NO_GUI and platform.system() == "Linux":
        logger.info(f"Start xvfb service")
        start_xvfb_display()

    api.launch(
        server_name="0.0.0.0" if cmd_opts.listen else "0.0.0.0",
        port=cmd_opts.port if cmd_opts.port else 5000,
    )


if __name__ == "__main__":
    api()
