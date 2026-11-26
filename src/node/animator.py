from .node import Node
from .entity.sprite.sprite import Sprite
from ..resources import Animation, AnimationKey, AnimationDict

from pprint import pprint


class Animator(Node):
    def __init__(
            self,
            sprite: Sprite,
            animations: AnimationDict
            ) -> None:
        super().__init__()
        self.sprite: Sprite = sprite
        self.animations: AnimationDict = animations
        self.current_animation: Animation = list(animations.items())[0][1]

    def update(self, dt: float) -> bool:
        "Returns whether the node is active and should be updated."
        if not self.active:
            return False

        self.sprite.image = self.current_animation.frame

        for child in self.children:
            child.update(dt)
        return True

    def play(self, key: AnimationKey, transition: bool = False) -> None:
        """Play an animation from the collection,
        selecting the specific animation using an ``AnimationKey``.

        Parameters
        ----------
        key : AnimationKey
            Which action to play in which direction.
        transition : bool, optional
            Whether to start the new animation from the beginning.
            By default, ``False``.
        """
        if key in self.animations:
            self.current_animation.stop()
            self.current_animation = self.animations[key]
            self.current_animation.play(transition)

    def stop(self) -> None:
        self.current_animation.stop()

    def pause(self) -> None:
        self.current_animation.pause()
