' Asynchronous subprocess helpers '
import asyncio
import logging
import subprocess

LOGGER = logging.getLogger('teslacam')

async def _check_output(cmd_line, stdout):
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd_line,
            stdout=stdout
        )
        await proc.wait()
        if proc.returncode:
            LOGGER.error('process %s failed', proc)
            raise subprocess.CalledProcessError(proc.returncode, cmd=' '.join(cmd_line))

        if proc.stdout:
            return await proc.stdout.read()

        return None

    except asyncio.CancelledError:
        if proc:
            LOGGER.debug('terminating process %s', proc)
            proc.terminate()
            await proc.wait()
            LOGGER.debug('%s terminated', proc)
        raise


async def check_call(cmd_line):
    ' Run subprocess using the provided command line tokens '
    return await _check_output(cmd_line, stdout=None)


async def check_output(cmd_line):
    ' Run subprocess using the provided command line tokens and return data '
    return await _check_output(cmd_line, stdout=asyncio.subprocess.PIPE)
