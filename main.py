import pumlpy.utils as utils


def main() -> None:
    
    # Create a UML object
    c = utils.create_package_uml('pumlpy')
    
    # Print the objects
    print(c.to_puml())


if __name__ == '__main__':
    main()
    