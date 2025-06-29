import os
import json
import argparse
from src.vectorizer import ChunkVectorizer

def main():
    # AutoDL arugments
    parser = argparse.ArgumentParser(description="Main entry point for AutoDL vectorization.")
    parser.add_argument("--config", type=str, default="config/training_config.json",
                        help="Path to the training configuration file.")
    
    # Get the path to the config file
    cli_args = parser.parse_args()
    config_path = cli_args.config
    
    # Load configuration from the specified file
    if not os.path.exists(config_path):
        print(f"Error: Configuration file not found at {config_path}")
        return
        
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Instantiate the vectorizer with the loaded configuration
    vectorizer = ChunkVectorizer(
        input_file=config['input'],
        db_directory=config['db'],
        model_name=config['model'],
        task=config['task'],
        truncate_dim=config.get('truncate_dim'),
        max_length=config['max_length'],
        device=config['device'],
        batch_size=config['batch_size']
    )
    
    # Run the vectorization process
    vectorizer.run()

if __name__ == "__main__":
    main() 