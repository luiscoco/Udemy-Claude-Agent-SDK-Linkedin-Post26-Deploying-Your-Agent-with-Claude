"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    question = data['question'].strip()
    if not question or len(question) > 2000:
        raise ValueError('Question must contain 1 to 2000 characters')
    answer = await agent.ask('request', 'Answer the supplied question in three concise bullets.', {'question': question},
                             'Check input validation, final run status, and a rollback path.')
    return {'answer': answer, 'release': 'lesson25-v1', 'request_validated': True}
