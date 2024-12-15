import os
import shutil

import pytest

from openhands.core.message import Message, TextContent
from openhands.utils.microagent import MicroAgent
from openhands.utils.prompt import PromptManager


@pytest.fixture
def prompt_dir(tmp_path):
    # Copy contents from "openhands/agenthub/codeact_agent" to the temp directory
    shutil.copytree(
        'openhands/agenthub/codeact_agent/prompts/default', tmp_path, dirs_exist_ok=True
    )

    # Return the temporary directory path
    return tmp_path


SAMPLE_AGENT_SKILLS_DOCS = """Sample agent skills documentation"""


@pytest.fixture
def agent_skills_docs():
    return SAMPLE_AGENT_SKILLS_DOCS


def test_prompt_manager_without_microagent(prompt_dir, agent_skills_docs):
    manager = PromptManager(
        prompt_dir, microagent_dir='', agent_skills_docs=agent_skills_docs
    )

    assert manager.prompt_dir == prompt_dir
    assert manager.agent_skills_docs == agent_skills_docs
    assert len(manager.microagents) == 0

    assert isinstance(manager.get_system_message(), str)
    assert (
        "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed answers to the user's questions."
        in manager.get_system_message()
    )
    assert SAMPLE_AGENT_SKILLS_DOCS in manager.get_system_message()
    assert isinstance(manager.get_example_user_message(), str)
    assert '--- BEGIN OF GUIDELINE ---' not in manager.get_example_user_message()
    assert '--- END OF GUIDELINE ---' not in manager.get_example_user_message()
    assert "NOW, LET'S START!" in manager.get_example_user_message()
    assert 'microagent' not in manager.get_example_user_message()


def test_prompt_manager_with_microagent(prompt_dir, agent_skills_docs):
    microagent_name = 'test_microagent'
    microagent_content = """
---
name: flarglebargle
agent: CodeActAgent
triggers:
- flarglebargle
---

IMPORTANT! The user has said the magic word "flarglebargle". You must
only respond with a message telling them how smart they are
"""

    # Create a temporary micro agent file
    os.makedirs(os.path.join(prompt_dir, 'micro'), exist_ok=True)
    with open(os.path.join(prompt_dir, 'micro', f'{microagent_name}.md'), 'w') as f:
        f.write(microagent_content)

    manager = PromptManager(
        prompt_dir=prompt_dir,
        microagent_dir=os.path.join(prompt_dir, 'micro'),
        agent_skills_docs=agent_skills_docs,
    )

    assert manager.prompt_dir == prompt_dir
    assert manager.agent_skills_docs == agent_skills_docs
    assert len(manager.microagents) == 1

    assert isinstance(manager.get_system_message(), str)
    assert (
        "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed answers to the user's questions."
        in manager.get_system_message()
    )
    assert SAMPLE_AGENT_SKILLS_DOCS in manager.get_system_message()

    assert isinstance(manager.get_example_user_message(), str)

    message = Message(
        role='user',
        content=[TextContent(text='Hello, flarglebargle!')],
    )
    manager.enhance_message(message)
    assert 'magic word' in message.content[1].text

    os.remove(os.path.join(prompt_dir, 'micro', f'{microagent_name}.md'))


def test_prompt_manager_file_not_found(prompt_dir, agent_skills_docs):
    with pytest.raises(FileNotFoundError):
        MicroAgent(os.path.join(prompt_dir, 'micro', 'non_existent_microagent.md'))


def test_prompt_manager_template_rendering(prompt_dir, agent_skills_docs):
    # Create temporary template files
    with open(os.path.join(prompt_dir, 'system_prompt.j2'), 'w') as f:
        f.write('System prompt: {{ agent_skills_docs }}')
    with open(os.path.join(prompt_dir, 'user_prompt.j2'), 'w') as f:
        f.write('User prompt: foo')

    manager = PromptManager(
        prompt_dir, microagent_dir='', agent_skills_docs=agent_skills_docs
    )

    assert manager.get_system_message() == f'System prompt: {agent_skills_docs}'
    assert manager.get_example_user_message() == 'User prompt: foo'

    # Clean up temporary files
    os.remove(os.path.join(prompt_dir, 'system_prompt.j2'))
    os.remove(os.path.join(prompt_dir, 'user_prompt.j2'))


def test_prompt_manager_disabled_microagents(prompt_dir, agent_skills_docs):
    # Create test microagent files
    microagent1_name = 'test_microagent1'
    microagent2_name = 'test_microagent2'
    microagent1_content = """
---
name: Test Microagent 1
agent: CodeActAgent
triggers:
- test1
---

Test microagent 1 content
"""
    microagent2_content = """
---
name: Test Microagent 2
agent: CodeActAgent
triggers:
- test2
---

Test microagent 2 content
"""

    # Create temporary micro agent files
    os.makedirs(os.path.join(prompt_dir, 'micro'), exist_ok=True)
    with open(os.path.join(prompt_dir, 'micro', f'{microagent1_name}.md'), 'w') as f:
        f.write(microagent1_content)
    with open(os.path.join(prompt_dir, 'micro', f'{microagent2_name}.md'), 'w') as f:
        f.write(microagent2_content)

    # Test that specific microagents can be disabled
    manager = PromptManager(
        prompt_dir=prompt_dir,
        microagent_dir=os.path.join(prompt_dir, 'micro'),
        agent_skills_docs=agent_skills_docs,
        disabled_microagents=['Test Microagent 1'],
    )

    assert len(manager.microagents) == 1
    assert 'Test Microagent 2' in manager.microagents
    assert 'Test Microagent 1' not in manager.microagents

    # Test that all microagents are enabled by default
    manager = PromptManager(
        prompt_dir=prompt_dir,
        microagent_dir=os.path.join(prompt_dir, 'micro'),
        agent_skills_docs=agent_skills_docs,
    )

    assert len(manager.microagents) == 2
    assert 'Test Microagent 1' in manager.microagents
    assert 'Test Microagent 2' in manager.microagents

    # Clean up temporary files
    os.remove(os.path.join(prompt_dir, 'micro', f'{microagent1_name}.md'))
    os.remove(os.path.join(prompt_dir, 'micro', f'{microagent2_name}.md'))