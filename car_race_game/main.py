"""Application entry point."""

from src.game import Game


def main() -> None:
    """Create and run the game instance."""
    game: Game = Game()
    game.run()


if __name__ == "__main__":
    main()
