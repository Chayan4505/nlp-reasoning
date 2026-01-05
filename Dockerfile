
# Use the official Pathway image
FROM pathwaycom/pathway:latest

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt ./

# Install dependencies
# Note: pathway is already in the base image, but requirements might have others (openai, pandas)
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Set PYTHONPATH to include src
ENV PYTHONPATH=/app/src

# Run the container with:
# docker run -it --rm -e GEMINI_API_KEY=your_key -e PATHWAY_LICENSE_KEY=your_key kdsh-track-a

CMD ["python", "src/run_inference.py"]
