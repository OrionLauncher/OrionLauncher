import sys
import logging
import tempfile
from pathlib import Path
from functools import wraps, partial
from typing import Callable, Any
try:
    from filelock import FileLock, AsyncFileLock, BaseAsyncFileLock, BaseFileLock
except ImportError:
    raise ImportError("filelock is not installed., Please install it using pip insall uv ")

logger = logging.getLogger(__name__)

__all__ = ["AppLock"]

class AppLock:
    """应用锁，防止应用二次启动
    
    这个类的作用是通过文件锁来实现同一个时间只能运行一个应用

    #! 由于tempfile.gettempdir()获取的临时路径会根据系统管理员和普通用户而不同，因此会导致应用锁失效
    
    Attributes:
        name (str): 应用名称
        lock_file (str): 文件锁文件名
        lock (BaseFileLock | BaseAsyncFileLock): 文件锁对象
        
    """
    
        
    def __init__(self, name: str = "app") -> None:
        self.name: str = name
        self.lock_file: Path = Path(tempfile.gettempdir()) / f"{name}.lock"
        self.lock: BaseAsyncFileLock | BaseFileLock | None = None
        logger.info(f"lock file path: {str(self.lock_file)}")
    
    @classmethod
    def lock_this(cls, main: Callable[..., Any] | None = None, *, name: str = "app"):
        """应用锁函数装饰器

        Args:
            main (Callable[..., Any] | None, optional): 应用入口函数. Defaults to None.
            name (str, optional): 应用名称. Defaults to "app_lock".
        
        Example:
        ... @AppLock.lock_this
        ... def main():
        ...     print("hello world")
        
        ... @AppLock.lock_this(name="myapp")
        ... def main():
        ...     print("hello world")
        """
        if main is None:
            return partial(cls.lock_this, name=name)
        @wraps(main)
        def _lock_this(*args, **kwargs):
            with cls(name):
                return main(*args, **kwargs)
        return _lock_this
    
    @classmethod
    def async_lock_this(cls, main: Callable[..., Any] | None = None, *, name: str = "app_lock"):
        """_summary_

        Args:
            main (Callable[..., Any] | None, optional): 应用入口函数. Defaults to None.
            name (str, optional): 应用名称. Defaults to "app_lock".

        Example:
        ... @AppLock.async_lock_this
        ... def main():
        ...     print("hello world")
        
        ... @AppLock.async_lock_this(name="myapp")
        ... def main():
        ...     print("hello world")
        """
        if main is None:
            return partial(cls.async_lock_this, name=name)
        @wraps(main)
        async def _async_lock_this(*args, **kwargs):
            async with cls(name):
                return await main(*args, **kwargs)
        return _async_lock_this
    
    def __enter__(self):
        try:
            self.lock = FileLock(self.lock_file)
            self.lock.acquire(timeout=0)
            logger.info("The app is started successfully")
        except TimeoutError:
            logger.warning("The app is already running")
            sys.exit(0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.lock, FileLock):
            self.lock.release()
            self.lock = None
        else:
            raise  TypeError("elf.lock is not an instance of FileLock")
        logger.info("The app is exited successfully")

        if exc_type is not None:
            logger.error(f"Exception in context: {exc_val}")
            
    async def __aenter__(self):
        try:
            self.lock = AsyncFileLock(self.lock_file)
            await self.lock.acquire(timeout=0)
            logger.info("The app is started successfully")
        except TimeoutError:
            logger.warning("The app is already running")
            sys.exit(0)
    
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if isinstance(self.lock, AsyncFileLock):
            await self.lock.release()
            self.lock = None
        else:
            raise TypeError("self.lock is not an instance of AsyncFileLock")
        logger.info("The app is exited successfully")

        if exc_type is not None:
            logger.error(f"Exception in context: {exc_val}")