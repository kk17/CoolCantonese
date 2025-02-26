# CoolCantonese WeChat Official Account Project
[![Build Status](https://travis-ci.org/kk17/CoolCantonese.svg)](https://travis-ci.org/kk17/CoolCantonese)

[中文](./README.md)

In order to help my friends to learn Cantonese, I develop this WeChat official account which provides text translation from many other languages to Cantonese and voice translation from Mandarin to Cantonese. You can use WeChat to scan the QR code below to subscribe to the official account.

![CoolCantonese](./docs/qrcode.jpg)

Support languages:
![Support languages](./docs/support_input_languages.png)

## System Requirements
- Python 3.12 or higher
- Docker 24.0 or higher (recommended for deployment)
- OCI-compliant container runtime

## Core Dependencies
- werobot>=1.13.1 - WeChat robot framework
- beautifulsoup4>=4.12.3 - HTML parsing
- lxml>=5.1.0 - XML processing
- redis>=5.0.1 - Session storage
- gunicorn>=21.2.0 - WSGI HTTP server

## Development Dependencies
- pytest>=8.0.0 - Testing framework
- black>=24.1.0 - Code formatting
- flake8>=7.0.0 - Code linting

## Configuration
Refer to `config.json.example` in the `coolcantonese/conf` directory.
If using Docker for deployment, refer to `.env.example`.

## Deployment
Recommended deployment using Docker with support for OCI format and multi-platform deployment:

1. Install Docker 24.0 or higher
2. Clone the project:
   ```bash
   git clone https://github.com/kk17/CoolCantonese.git
   cd CoolCantonese
   ```
3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env file with required parameters
   ```
4. Start the service:
   ```bash
   docker compose up -d
   ```

## Local Development
1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate  # Windows
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r dev-requirements.txt
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Testing
- Unit Tests: Run test suite using pytest
- Integration Tests: Use [ushuz/weixin-simulator](https://github.com/ushuz/weixin-simulator) for WeChat interface testing
- Code Quality:
  ```bash
  black .  # Format code
  flake8  # Lint code
  ```

## Credits
1. [Ekho](http://www.eguidedog.net/cn/ekho_cn.php) - Text To Speech (TTS) software supporting Cantonese and Mandarin
2. [whtsky/WeRoBot](https://github.com/whtsky/WeRoBot) - Python WeChat robot framework

## Looking for Frontend Developers
We want to develop a WeChat mini program and an official website for this project. Due to limited frontend skills and time constraints, we are looking for help from frontend developers. If you are a frontend developer interested in this project, please contact us.

## Contributing
Pull requests and issues are welcome. This project uses Python 3.12 and modern Python development practices, including:
- Type hints
- Modern exception handling
- Code quality tools
- Comprehensive test coverage

## License
This project is licensed under the MIT License - see the LICENSE file for details.