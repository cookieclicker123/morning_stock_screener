"""Main application entry point for Morning Stock Screener."""

import asyncio
import os
import sys


from .config import get_settings
from .llm import OpenAIWrapper
from .models.llm import LLMRequest


async def chat_interface():
    """Simple chat interface for testing the LLM wrapper."""
    print("🤖 Morning Stock Screener - LLM Test Interface")
    print("=" * 50)
    print("Type 'quit' to exit, 'help' for commands")
    print()

    # Initialize LLM wrapper
    try:
        settings = get_settings()
        llm = OpenAIWrapper(settings.openai_api_key, settings.openai_model)
        print(f"✅ Connected to OpenAI using model: {settings.openai_model}")
    except Exception as e:
        print(f"❌ Failed to initialize LLM wrapper: {e}")
        print("Please check your OPENAI_API_KEY environment variable")
        return

    print()

    while True:
        try:
            user_input = input("💬 You: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == "help":
                print("\n📚 Available commands:")
                print("  help     - Show this help message")
                print("  quit     - Exit the application")
                print("  clear    - Clear the screen")
                print("  model    - Show current model")
                print("  system   - Set custom system prompt")
                print()
                continue
            elif user_input.lower() == "clear":
                os.system("clear" if os.name == "posix" else "cls")
                continue
            elif user_input.lower() == "model":
                print(f"🤖 Current model: {llm.default_model}")
                continue
            elif user_input.lower() == "system":
                system_prompt = input("🔧 Enter system prompt: ").strip()
                if system_prompt:
                    # Store system prompt for future use
                    print(f"✅ System prompt set: {system_prompt[:50]}...")
                continue
            elif not user_input:
                continue

            # Default system prompt for testing
            system_prompt = """You are a helpful AI assistant. You can help with general questions and provide informative responses. 
            Keep responses concise and helpful."""

            # Create LLM request
            request = LLMRequest(
                system_prompt=system_prompt,
                user_prompt=user_input,
                temperature=0.7,
                max_tokens=1000,
            )

            print("🤔 Thinking...")

            # Generate response
            response = await llm.generate_response(request)

            if response.success:
                print(f"\n🤖 Assistant: {response.content}")
                print("\n📊 Response Info:")
                print(f"   Model: {response.model_used}")
                print(f"   Tokens: {response.tokens_used}")
                print(f"   Time: {response.response_time_ms:.2f}ms")
            else:
                print(f"❌ Error: {response.error_message}")

            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            print()


def main():
    """Main application entry point."""
    try:
        asyncio.run(chat_interface())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
