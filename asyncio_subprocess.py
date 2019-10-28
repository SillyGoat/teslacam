import asyncio
import logging
import subprocess

logging.basicConfig(format='%(asctime)-15s %(message)s', level=logging.INFO)
LOGGER = logging.getLogger('asyncio_subprocess')

async def _check_output(cmd_line, stdout):
    proc = await asyncio.create_subprocess_exec(
        *cmd_line,
        stdout=stdout
    )
    try:
        await proc.wait()
        if proc.returncode:
            LOGGER.error(f'process {proc} failed')
            raise subprocess.CalledProcessError(proc.returncode, cmd=' '.join(cmd_line))

        if proc.stdout:
            return await proc.stdout.read()

        return None

    except asyncio.CancelledError:
        LOGGER.warning(f'terminating process {proc}')
        proc.terminate()
        raise


async def check_call(cmd_line):
    ' Run subprocess using the provided command line tokens '
    return await _check_output(cmd_line, stdout=None)


async def check_output(cmd_line):
    ' Run subprocess using the provided command line tokens and return data '
    return await _check_output(cmd_line, stdout=asyncio.subprocess.PIPE)
