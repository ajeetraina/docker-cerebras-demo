# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""LLM Auditor for verifying & refining LLM-generated answers using the web."""

from . import agent
import os
import logging, litellm
# Set the base URL for the OpenAI API to the Docker Model Runner URL
os.environ.setdefault("OPENAI_BASE_URL", os.getenv("DOCKER-MODEL-RUNNER_URL"))
# Set the API key to a dummy value since it's not used
os.environ.setdefault("OPENAI_API_KEY","not-used")

# Enable debug logging 
logging.basicConfig(
    level=logging.DEBUG,                         # ADK, FastAPI, everything
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    force=True,                                  # override ADK defaults
)
logging.getLogger("google.adk").setLevel(logging.DEBUG)
logging.getLogger("LiteLLM").setLevel(logging.DEBUG)
litellm.set_verbose = True                       # raw HTTP <--> model
