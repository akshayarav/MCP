# Simple hello world program
print("Hello, World!")

# You can also make it interactive
name = input("What's your name? ")
print(f"Hello, {name}!")

# Or create a function
def greet(name="World"):
    """Simple greeting function"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet())
    print(greet("Jane Doe"))
