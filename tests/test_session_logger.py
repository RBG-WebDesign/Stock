# tests/test_session_logger.py
import asyncio
import json
import shutil
import pytest
from tqa.utils.session_logger import SessionLogger

from config.settings import settings

@pytest.mark.asyncio
async def test_session_logger_concurrency():
    # Ensure any existing run directory for this test is clean
    session_id = "test_concurrency_session"
    session_dir = settings.REPORTS_DIR / "runs" / session_id
    if session_dir.exists():
        try:
            shutil.rmtree(session_dir)
        except Exception:
            # If still locked from previous crashes, try to close logging handles
            import logging
            for logger_name in list(logging.Logger.manager.loggerDict.keys()):
                if logger_name.startswith("session."):
                    logger = logging.getLogger(logger_name)
                    for h in list(logger.handlers):
                        h.close()
                        logger.removeHandler(h)
            shutil.rmtree(session_dir)
            
    session = SessionLogger(session_id=session_id)
    
    try:
        # Write initial configuration
        await session.log_config({"universe_limit": 100})
        assert session.config_log_path.exists()
        
        # We will run multiple concurrent tasks updating funnel stats and logging config
        async def run_update(i):
            session.update_funnel_stats(
                universe_count=1000 + i,
                fundamental_passed_count=500 + i,
                technical_passed_count=100 + i,
                final_watchlist_count=50 + i
            )
            # Sleep a tiny bit to yield control
            await asyncio.sleep(0.001)

        async def run_log(i):
            await session.log_config({
                "universe_limit": 100,
                "min_eps_growth": 5.0 + i,
                "min_rev_growth": 10.0 + i
            })
            await asyncio.sleep(0.001)

        # Gather many tasks to execute concurrently
        tasks = []
        for i in range(50):
            tasks.append(run_update(i))
            tasks.append(run_log(i))
            
        await asyncio.gather(*tasks)
        
        # Read the final file and make sure it is valid JSON
        assert session.config_log_path.exists()
        with open(session.config_log_path, "r") as f:
            config = json.load(f)
            
        # Verify the structure is correct
        assert "universe_limit" in config
        assert "funnel_stats" in config
        assert "final_watchlist_count" in config["funnel_stats"]
    finally:
        # Cleanup
        session.close()
        if session.session_dir.exists():
            shutil.rmtree(session.session_dir)
