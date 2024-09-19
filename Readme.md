# Proofly (aka WebAnalyzer1)

Proofly is a generative AI-enabled tool designed for website proofreading and caution word detection. Leveraging the power of Large Language Models (LLMs), Proofly ensures accurate proofreading. It also supports reading and proofreading of PDF, DOC, and TXT files.

## Features

- **Spelling Correction**: Automatically corrects spelling errors.
- **Grammar Correction**: Identifies and corrects grammatical mistakes.
- **US to UK English Conversion**: Converts US English to UK English for consistency.

## Getting Started

Follow these instructions to set up and run Proofly on your local machine.

### Prerequisites

- Python 3.8 or higher
- Node.js 14.x or higher
- npm (Node Package Manager)

### prepare screens
tmux (short for "Terminal Multiplexer") is a terminal management tool that allows you to run multiple terminal sessions inside a single terminal window. It's especially useful for managing long-running processes on remote servers or when you want to keep sessions open even after disconnecting.
1. To presistance running you need to install tmux.
```
sudo apt install tmux
```
2. You need to create tmux screens when PC reboots.
```
tmux new -s frontend
tmux new -s backend
```
### Installation
0. **Setup Screens**
   To run the application with concestancy on ssh Server you need to create screen. Using tmux create two 
   screens frontend and backend
1. **Clone the Repository**

   ``` 
   git clone https://github.com/yourusername/proofly.git
   cd proofly
   ```

2. **Install Backend Dependencies**

   Navigate to the root directory and install the necessary Python packages:

   ``` 
   pip install -r requirements.txt
   ```

3. **Install Frontend Dependencies**

   Navigate to the UI directory:

   ```bash
   cd UI/proofly
   npm install
   ```

### Configuration

1. **Environment Variables**

   Add your OpenAI and Firecrawl API keys to the `.env` file located inside the `src` folder. Here’s a sample `.env` file:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   FIRECRAWL_API_KEY=your_firecrawl_api_key
   ```

### Running the Application


1. **Start the FastAPI Server**
   It will run the appliacation over http://0.0.0.0:8000/
   Navigate to the project’s root directory and start the FastAPI server:
   

   Go to backend stream 
   ```
   tmux a -t backend
   ```

   ```
   python server.py
   ```

2. **Start the Frontend**

   Navigate to the UI directory and start the React frontend:
   Since port 80 have some premssion issue that why a sudo.

   Go to backend stream 
   ```
   tmux a -t frontend
   ```

    ```
   cd UI/proofly
   sudo PORT=80 npm start
   ```

3. **Access the Application**

   Once both the server and UI are running, you can access Proofly by opening your web browser and navigating to:

   ```
   http://localhost:80
   ```

## Usage

- **Website Proofreading**: Paste the URL of the website you want to proofread, and Proofly will analyze the content for spelling, grammar, and caution words.
- **Document Proofreading**: Upload your PDF, DOC, or TXT file for proofreading.

## Credits

Developed by Muhammad Ali Abbas