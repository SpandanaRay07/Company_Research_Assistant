import os
import sys
from .research_agent import CompanyResearchAgent
from .account_plan import AccountPlanGenerator
from dotenv import load_dotenv

load_dotenv()


def chat_mode(agent: CompanyResearchAgent):
    print("=" * 60)
    print("👋 Hello there! I am a Company Research Assistant, how may i help you ?")
    print("You can ask follow-up questions anytime - I'll remember our conversation")
    print("Type 'quit' to exit when you're done")
    print("=" * 60)
    print()
    
    current_plan = None
    conversation_context = []
    
    while True:
        try:
            query = input("You: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("\nThanks for chatting! Feel free to come back anytime if you need more company research. Have a great day! 😊")
                break
            
            if not query:
                continue
            
            if 'generate plan' in query.lower() or 'create plan' in query.lower():
                if current_plan:
                    print("\n" + "=" * 60)
                    print(current_plan.to_markdown())
                    print("=" * 60)
                else:
                    print("I'd love to help! Please research a company first, then I can create an account plan for you.")
                continue
            
            if 'edit' in query.lower() and current_plan:
                print("\nWhich section would you like to edit?")
                print("Available sections: overview, business, products, market, financial, opportunities, challenges, recommendations, next_steps")
                section = input("Section name: ").strip().lower()
                
                if section:
                    section_map = {
                        'overview': 'company_overview',
                        'business': 'business_model',
                        'products': 'key_products_services',
                        'market': 'market_position',
                        'financial': 'financial_highlights',
                        'opportunities': 'opportunities',
                        'challenges': 'challenges',
                        'recommendations': 'recommendations',
                        'next_steps': 'next_steps'
                    }
                    
                    section_key = section_map.get(section, section)
                    if section_key in current_plan.sections:
                        print(f"\nCurrent content:\n{current_plan.get_section(section_key) or '(empty)'}")
                        print("\nEnter new content (press Enter twice to finish):")
                        new_content = []
                        while True:
                            line = input()
                            if not line and new_content and not new_content[-1]:
                                break
                            new_content.append(line)
                        
                        new_text = '\n'.join(new_content).strip()
                        if new_text:
                            current_plan.update_section(section_key, new_text)
                            print("✓ Section updated!")
                    else:
                        print("❌ Section not found!")
                continue
            
            is_followup = len(conversation_context) > 0 and not any(cmd in query.lower() for cmd in ['generate plan', 'edit', 'create plan'])
            
            print("\n🔍 Let me get that information for you...")
            
            if is_followup:
                result = agent.handle_followup(query, conversation_context)
            else:
                def ask_user(question):
                    print(f"\n{question}")
                    return input("Your answer: ").strip().lower()
                
                result = agent.research_company(query, ask_user_callback=ask_user)
            
            if result['success']:
                print("\n" + "=" * 60)
                print("Here's what I found:")
                print("=" * 60)
                print()
                print(result['response'])
                print()
                
                if result.get('wikipedia_sources') or result.get('news_sources') or result.get('linkedin_source') or result.get('web_sources'):
                    print("Sources I used:")
                    if result.get('wikipedia_sources'):
                        for i, source in enumerate(result['wikipedia_sources'][:3], 1):
                            print(f"  {source.get('title', 'Unknown')}")
                    
                    if result.get('news_sources'):
                        for i, article in enumerate(result['news_sources'], 1):
                            print(f"  {article.get('title', 'Unknown')} - {article.get('source', 'Unknown')}")
                    
                    if result.get('linkedin_source'):
                        print(f"  {result['linkedin_source'].get('title', 'Unknown')} (LinkedIn)")
                    
                    if result.get('web_sources'):
                        for i, web_result in enumerate(result['web_sources'][:3], 1):
                            print(f"  {web_result.get('title', 'Unknown')}")
                    
                    print(f"\n✨ Found information from {result.get('sources_count', 0)} sources total!")
                
                if result.get('deeper_research') and result['deeper_research'].get('success'):
                    print("\nHere's what I found when digging deeper:")
                    print(result['deeper_research'].get('clarification', ''))
                
                print("=" * 60)
                
                conversation_context.append(result)
                
                print("\n💡 Would you like me to create an account plan for this company? (yes/no)")
                response = input("Your answer: ").strip().lower()
                
                if response in ['yes', 'y']:
                    print("\nGreat! Let me create a comprehensive account plan for you...")
                    plan_generator = AccountPlanGenerator(agent.client)
                    plan = plan_generator.generate_plan(
                        company_name=result.get('company_name', 'Unknown'),
                        research_context=result.get('response', ''),
                        conflicts=[]
                    )
                    
                    for source in result.get('sources', []):
                        plan.add_source(source)
                    
                    current_plan = plan
                    print("\nPerfect! I've created your account plan!")
                    print("\n" + "=" * 60)
                    print(plan.to_markdown())
                    print("=" * 60)
                    
                    print("\n💡 Save this plan to a file? (yes/no)")
                    save_response = input("Your answer: ").strip().lower()
                    if save_response in ['yes', 'y']:
                        filename = f"{result.get('company_name', 'plan').replace(' ', '_')}_account_plan.md"
                        try:
                            with open(filename, 'w') as f:
                                f.write(plan.to_markdown())
                            print(f"✓ Saved to {filename}")
                        except Exception as e:
                            print(f"❌ Error saving: {e}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error occurred')}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}\n")


def voice_mode(agent: CompanyResearchAgent):
    try:
        import speech_recognition as sr 
        from gtts import gTTS
        import pygame
        import io
    except ImportError:
        print("❌ Voice mode needs: pip install SpeechRecognition gtts pygame")
        print("Switching to chat mode...")
        chat_mode(agent)
        return
    
    print("=" * 60)
    print("Company Research Agent - Voice Mode")
    print("Say 'quit' when you're done")
    print("=" * 60)
    print()
    
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    pygame.mixer.init()
    
    print("Setting up microphone...")
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
    print("All set! I'm ready to listen. Ask me about any company!\n")
    
    while True:
        try:
            print("🎤 Listening...")
            with microphone as source:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=25)
            
            try:
                query = recognizer.recognize_google(audio)
                print(f"You said: {query}\n")
                
                if query.lower() in ['quit', 'exit']:
                    print("Thanks for chatting! Have a great day! 😊")
                    break
                
                print("🔍 Let me find that information for you...")
                result = agent.research_company(query, ask_user_callback=None, voice_mode=True)
                
                if result['success']:
                    response_text = result['response']
                    print(f"\nHere's what I found:\n{response_text}\n")
                    
                    tts = gTTS(text=response_text, lang='en', slow=False)
                    audio_buffer = io.BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    
                    pygame.mixer.music.load(audio_buffer)
                    pygame.mixer.music.play()
                    
                    while pygame.mixer.music.get_busy():
                        pygame.time.wait(100)
                else:
                    print(f"Oops! {result.get('error')}")
                    print("Try asking about the company in a different way!")
                
                print()
                
            except sr.UnknownValueError:
                print("I didn't catch that. Could you try again?\n")
            except sr.RequestError as e:
                print(f"Hmm, there was an issue with speech recognition. Let me try again...\n")
                
        except sr.WaitTimeoutError:
            print("I'm listening... feel free to ask your question!\n")
        except KeyboardInterrupt:
            print("\n\nThanks for using the voice assistant! Have a great day! 😊")
            break
        except Exception as e:
            print(f"Oops! Something went wrong: {str(e)}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Company Research Agent")
    parser.add_argument('--mode', choices=['chat', 'voice'], default='chat',
                       help='Mode: chat (default) or voice')
    parser.add_argument('--api-key', type=str,
                       help='OpenAI API key (or set OPENAI_API_KEY env variable)')
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OpenAI API key required!")
        print("Options:")
        print("  1. Set it in .env file (OPENAI_API_KEY=sk-...)")
        print("  2. Set OPENAI_API_KEY environment variable")
        print("  3. Use --api-key command line argument")
        sys.exit(1)
    
    try:
        agent = CompanyResearchAgent(openai_api_key=api_key)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
    
    if args.mode == 'voice':
        voice_mode(agent)
    else:
        chat_mode(agent)


if __name__ == "__main__":
    main()
