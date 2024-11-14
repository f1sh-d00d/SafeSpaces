from dotenv import load_dotenv
import os
import openai
import textwrap

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("No OpenAI API key found. Please set OPENAI_API_KEY environment variable.")

def read_text_file(file_path):
    """Read text from a txt file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def save_summary_txt(summary, output_path):
    """Save the summary to a txt file"""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(summary)

def summarize_text(text):
    """Use OpenAI to summarize the text"""
    try:
        client = openai.OpenAI(api_key=api_key)  # Pass API key here
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Fixed model name typo (was "gpt-4o-mini")
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates clear, concise summaries."},
                {"role": "user", "content": f"Please provide a concise summary of the following text:\n\n{text}"}
            ],
            max_tokens=1000,
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error during summarization: {e}")
        return None

def main(input_txt_path, output_txt_path):
    """Main function to handle the summarization process"""
    try:
        # Read text from input file
        print("Reading text file...")
        text = read_text_file(input_txt_path)
        
        # If the text is very long, we might need to process it in chunks
        if len(text) > 4000:  # Adjust this threshold as needed
            chunks = textwrap.wrap(text, 4000)
            summaries = []
            for chunk in chunks:
                chunk_summary = summarize_text(chunk)
                if chunk_summary:
                    summaries.append(chunk_summary)
            final_summary = summarize_text("\n".join(summaries))
        else:
            final_summary = summarize_text(text)
        
        if final_summary:
            # Save summary to txt file
            print("Creating summary file...")
            save_summary_txt(final_summary, output_txt_path)
            print(f"Summary file created successfully at {output_txt_path}")
        else:
            print("Failed to generate summary")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Example usage
    input_txt = r"SafeSpaces\Final_Project\notes.txt"  # Path to your input text file
    output_txt = r"SafeSpaces\Final_Project\summary.txt"  # Path for the output text file
    main(input_txt, output_txt)

