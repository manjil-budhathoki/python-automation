# Read the file and process each line
with open('text.txt', 'r') as file:
    lines = file.readlines()

# Strip whitespace/newlines, wrap in quotes, and join with commas
formatted = ', '.join(f'"{line.strip()}"' for line in lines if line.strip())

print(formatted)   