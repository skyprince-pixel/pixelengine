from pixelengine import (
    Scene, PixelConfig, Circle, Line, Sprite, TypeWriter,
    MoveTo, MoveBy, FadeIn, Sequence, PixelText, SoundFX, Grid,
    ParticleEmitter, Outline, Rect, FadeOut, ColorShift, Rotate
)
from pixelengine.voiceover import VoiceOver

class NonEuclideanGeometry(Scene):
    def construct(self):
        # 1. Intro
        self.intro_scene()
        
        # 1.5 History (NEW)
        self.history_scene()
        
        # 2. Spherical Geometry
        self.spherical_scene()

        # 3. Hyperbolic Geometry
        self.hyperbolic_scene()
        
        # 3.5 Tiling (NEW)
        self.tiling_scene()
        
        # 4. General Relativity
        self.relativity_scene()
        
        # 4.5 Shape of the Universe (NEW)
        self.universe_shape_scene()
        
        # 5. Conclusion
        self.conclusion_scene()

    def intro_scene(self):
        # Background Grid
        grid = Grid(cell_size=16)
        self.add(grid)
        self.play(FadeIn(grid), duration=1.0)
        
        self.play_sound(SoundFX.powerup())
        title = PixelText("NON-EUCLIDEAN", x=128, y=60, align="center")
        subtitle = PixelText("GEOMETRY", x=128, y=80, align="center")
        self.add(title, subtitle)
        self.play(TypeWriter(title), duration=1.5)
        self.play(TypeWriter(subtitle), duration=1.0)
        self.wait(1.0)
        
        self.play_voiceover(
            "Hello, and welcome to a journey beyond the flat sheet of paper. "
            "For over two thousand years, mathematical reality was dominated by one man: Euclid.",
            voice="am_adam"
        )
        
        self.play(FadeOut(title), FadeOut(subtitle), duration=1.0)
        
        # Draw Euclid's 5th postulate
        self.play_voiceover(
            "Euclid's geometry is what we all learn in school. "
            "It consists of points, lines, and shapes on a perfectly flat surface.",
            voice="am_adam"
        )
        
        line1 = Line(x1=20, y1=50, x2=236, y2=50, color="#FF004D")
        line2 = Line(x1=20, y1=90, x2=236, y2=90, color="#FF004D")
        
        self.play_sound(SoundFX.jump())
        self.add(line1, line2)
        self.play(Sequence(FadeIn(line1), FadeIn(line2)), duration=2.0)
        
        self.play_voiceover(
            "The crown jewel of his system was the famous Fifth Postulate, also known as the Parallel Postulate. "
            "It states that parallel lines will NEVER intersect, no matter how far you extend them across the universe.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "And inside this flat universe, the sum of the angles of ANY triangle is exactly 180 degrees. "
            "Always. No exceptions. It felt so completely intuitive and pure, that mathematicians accepted it as an absolute truth of the universe.",
            voice="am_adam"
        )
        
        # Draw a triangle
        self.play(FadeOut(line1), FadeOut(line2), duration=0.5)
        triangle = Line(x1=128, y1=40, x2=80, y2=100, color="#00E436")
        triangle2 = Line(x1=80, y1=100, x2=176, y2=100, color="#00E436")
        triangle3 = Line(x1=176, y1=100, x2=128, y2=40, color="#00E436")
        self.add(triangle, triangle2, triangle3)
        self.play(FadeIn(triangle), duration=0.5)
        self.play(FadeIn(triangle2), duration=0.5)
        self.play(FadeIn(triangle3), duration=0.5)
        
        sum_text = PixelText("180 DEGREES", x=128, y=120, align="center", color="#FFFF00")
        self.add(sum_text)
        self.play(TypeWriter(sum_text), duration=1.0)
        
        self.play_voiceover(
            "But then, in the 19th century, rebel mathematicians like Gauss, Bolyai, and Lobachevsky started asking a dangerous question. "
            "What if we throw the fifth postulate away? What if the universe isn't flat?",
            voice="am_adam"
        )
        
        self.play(FadeOut(triangle), FadeOut(triangle2), FadeOut(triangle3), FadeOut(sum_text), FadeOut(grid), duration=1.0)

    def history_scene(self):
        bg = Rect(width=256, height=144, x=0, y=0, color="#1D2B53")
        self.add(bg)
        self.play(FadeIn(bg), duration=1.0)
        
        self.play_voiceover(
            "To understand why this discovery was so revolutionary, we have to travel back to the 18th century. "
            "For generations, mathematicians weren't looking for a new geometry. They were trying to save Euclid's.",
            voice="am_adam"
        )
        
        par_text = PixelText("POSTULATE 5", x=128, y=40, align="center", color="#FF004D")
        self.add(par_text)
        self.play(TypeWriter(par_text), duration=1.0)
        
        self.play_voiceover(
            "The Fifth Postulate always felt... off. While the other four postulates were short, simple, and self-evident, "
            "the fifth was long and wordy. It felt more like a theorem that should be proven, rather than an unshakeable assumption.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "In 1733, an Italian Jesuit priest named Giovanni Girolamo Saccheri attempted to prove the postulate by contradiction. "
            "He assumed it was FALSE, hoping that the resulting geometry would be so ridiculous and illogical that it would eventually implode.",
            voice="am_adam"
        )
        
        self.play_sound(SoundFX.powerup())
        saccheri = PixelText("SACCHERI", x=128, y=80, align="center")
        self.add(saccheri)
        self.play(TypeWriter(saccheri), duration=1.0)
        
        self.play_voiceover(
            "Saccheri explored two 'wrong' universes. One where parallel lines always eventually meet—that's our spherical space. "
            "And one where parallel lines spread apart—our hyperbolic space.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "He found hundreds of strange properties, but he never actually found an internal logical contradiction. "
            "Afraid of his own discovery, he claimed the new geometries 'repelled' the truth and died thinking he had failed.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "It took another century before Carl Friedrich Gauss—the 'Prince of Mathematicians'—privately admitted that these 'absurd' geometries were perfectly consistent. "
            "He was so afraid of the controversy that he never published his work, leaving the credit to Bolyai and Lobachevsky.",
            voice="am_adam"
        )
        
        gauss = PixelText("GAUSS", x=128, y=110, align="center", color="#FFFF00")
        self.add(gauss)
        self.play(TypeWriter(gauss), duration=1.0)
        
        self.play_voiceover(
            "They finally realized that you can't prove the fifth postulate. It's an independent choice. "
            "Euclidean geometry is just ONE possible way the universe could work. It's not the only way.",
            voice="am_adam"
        )
        
        self.play(FadeOut(par_text), FadeOut(saccheri), FadeOut(gauss), FadeOut(bg), duration=1.0)

    def spherical_scene(self):
        bg = Rect(width=256, height=144, x=0, y=0, color="#1D2B53")
        self.add(bg)
        self.play(FadeIn(bg), duration=1.0)
        
        self.play_voiceover(
            "Welcome to the first realm of Non-Euclidean geometry: Elliptic Geometry, also known as Spherical Geometry.",
            voice="am_adam"
        )
        
        sphere = Circle(radius=50, x=128, y=72, color="#29ADFF")
        self.add(sphere)
        self.play(FadeIn(sphere), duration=1.5)
        
        self.play_voiceover(
            "Imagine a world that exists entirely on the surface of a perfect sphere. "
            "Like the Earth, for example.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "On a sphere, there are no straight lines as we know them. "
            "The closest thing to a straight line here is a Great Circle, which is the largest possible circle drawn around the sphere.",
            voice="am_adam"
        )
        
        equator = Rect(width=100, height=2, x=78, y=71, color="#FF004D")
        self.add(equator)
        self.play(FadeIn(equator), duration=1.0)
        equator_text = PixelText("EQUATOR", x=128, y=82, align="center")
        self.add(equator_text)
        self.play(TypeWriter(equator_text), duration=0.5)
        
        self.play_voiceover(
            "Think of the equator. Now, let's draw two lines of longitude completely perpendicular to the equator, shooting straight up towards the North Pole.",
            voice="am_adam"
        )
        
        line1 = Rect(width=2, height=50, x=100, y=22, color="#FFA300")
        line2 = Rect(width=2, height=50, x=154, y=22, color="#FFA300")
        self.add(line1, line2)
        self.play(FadeIn(line1), FadeIn(line2), duration=1.0)
        
        self.play_voiceover(
            "At the equator, these two lines are completely parallel. In a flat universe, they would never touch. "
            "But here, because of the positive curvature of the space, they eventually crash into each other exactly at the North Pole!",
            voice="am_adam"
        )
        
        self.play(MoveTo(line1, x=127, y=22), MoveTo(line2, x=129, y=22), duration=1.5)
        self.play_sound(SoundFX.explosion())
        sparks = ParticleEmitter.sparks(x=128, y=22)
        self.add(sparks)
        self.wait(1.0)
        
        self.play_voiceover(
            "This shatters Euclid's fifth postulate. And it creates a bizarre new reality for triangles. "
            "If you form a triangle with the equator and these two lines of longitude, the sum of the angles is GREATER than 180 degrees. You can easily have a triangle with THREE 90-degree angles, adding up to 270 degrees!",
            voice="am_adam"
        )
        
        self.play(FadeOut(equator), FadeOut(line1), FadeOut(line2), FadeOut(equator_text), duration=1.0)
        
        self.play_voiceover(
            "This isn't just abstract math. Airplane pilots and sea navigators must use Spherical geometry every single day. "
            "If they used flat maps, airplanes would fly completely off course.",
            voice="am_adam"
        )
        
        self.play(FadeOut(sphere), FadeOut(bg), duration=1.0)

    def hyperbolic_scene(self):
        bg = Rect(width=256, height=144, x=0, y=0, color="#000000")
        self.add(bg)
        self.play(FadeIn(bg), duration=1.0)
        
        self.play_voiceover(
            "Now let's flip the curvature. Welcome to Hyperbolic Geometry, a space with negative curvature.",
            voice="am_adam"
        )
        
        saddle = PixelText("SADDLE SHAPE", x=128, y=30, align="center", color="#FF77A8")
        self.add(saddle)
        self.play(TypeWriter(saddle), duration=1.0)
        
        self.play_voiceover(
            "Imagine the shape of a horse's saddle, or a Pringles potato chip. "
            "In this space, things get even more mind-bending.",
            voice="am_adam"
        )
        
        c1 = Circle(radius=20, x=128, y=72, color="#00E436")
        self.add(c1)
        self.play(FadeIn(c1), duration=1.0)
        
        self.play_voiceover(
            "If you draw a straight line, and place a point next to it, Euclid said you can only draw ONE parallel line through that point. "
            "But in Hyperbolic geometry, you can draw an INFINITE number of parallel lines through that single point without ever intersecting the first line!",
            voice="am_adam"
        )
        
        lines = []
        for i in range(10):
            l = Rect(width=200, height=1, x=28, y=60 + i*3, color="#FF004D")
            self.add(l)
            lines.append(l)
            
        for l in lines:
            self.play_sound(SoundFX.coin())
            self.play(FadeIn(l), duration=0.1)
            
        self.wait(1.0)
        
        self.play_voiceover(
            "And what about triangles? In a hyperbolic world, the angles of a triangle add up to LESS than 180 degrees. "
            "The larger the triangle gets, the thinner and sharper its corners become, approaching zero degrees.",
            voice="am_adam"
        )
        
        for l in lines:
            self.play(FadeOut(l), duration=0.0)
            
        self.play_voiceover(
            "It sounds like a mathematical illusion, but hyperbolic geometry strongly describes the structure of some fascinating natural phenomena, like the growth patterns of coral reefs and the leaves of kale.",
            voice="am_adam"
        )
        
        self.play(FadeOut(c1), FadeOut(saddle), FadeOut(bg), duration=1.0)

    def tiling_scene(self):
        bg = Rect(width=256, height=144, x=0, y=0, color="#1D2B53")
        self.add(bg)
        self.play(FadeIn(bg), duration=1.0)
        
        self.play_voiceover(
            "Hyperbolic geometry isn't just about single lines or triangles. It changes how an entire space can be tiled. "
            "In our everyday Euclidean world, you can tile a floor with squares, or triangles, or hexagons.",
            voice="am_adam"
        )
        
        # Draw a simple grid
        g = Grid(cell_size=16)
        self.add(g)
        self.play(FadeIn(g), duration=1.0)
        
        self.play_voiceover(
            "But you can't tile a flat floor with pentagons or heptagons without leaving ugly gaps or having them overlap. "
            "The geometry of the space simply won't allow it.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "However, in a Hyperbolic universe, because there is 'more space' as you move outward from any point, "
            "you can tile the entire infinite plane with perfect heptagons, or any other polygon you can imagine.",
            voice="am_adam"
        )
        
        # Simulate tiles with circles/rects
        tiles = []
        for i in range(5):
            for j in range(3):
                t = Circle(radius=10, x=30 + i*45, y=30 + j*45, color="#FF004D", filled=False)
                self.add(t)
                tiles.append(t)
                
        self.play(Sequence(*[FadeIn(t) for t in tiles]), duration=2.0)
        
        self.play_voiceover(
            "This leads to the beautiful Poincaré Disk models you might have seen in the art of M.C. Escher. "
            "The shapes look like they are getting smaller and smaller as they approach the edge, but in their own "
            "geometry, they are all exactly the same size, repeating forever into infinity.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "This 'infinite' property of small spaces is why hyperbolic geometry is being used today to map "
            "complex networks like the Internet and the neural connections in our brains. "
            "Hyperbolic space is simply better at holding large amounts of branching data.",
            voice="am_adam"
        )
        
        self.play(FadeOut(bg), FadeOut(g), *[FadeOut(t) for t in tiles], duration=1.0)

    def relativity_scene(self):
        bg = Rect(width=256, height=144, x=0, y=0, color="#1D2B53")
        grid = Grid(cell_size=16)
        self.add(bg, grid)
        self.play(FadeIn(bg), FadeIn(grid), duration=1.0)
        
        self.play_voiceover(
            "For decades, these non-Euclidean worlds were treated as nothing more than fun thought experiments, totally disconnected from real physics.",
            voice="am_adam"
        )
        
        einstein = PixelText("ALBERT EINSTEIN", x=128, y=72, align="center")
        self.add(einstein)
        self.play(TypeWriter(einstein), duration=1.0)
        self.play_sound(SoundFX.powerup())
        self.play(ColorShift(einstein, to_color="#FFFF00"), duration=0.5)
        
        self.play_voiceover(
            "That all changed in 1915, when Albert Einstein published his General Theory of Relativity.",
            voice="am_adam"
        )
        
        self.play(FadeOut(einstein), duration=0.5)
        
        sun = Circle(radius=30, x=128, y=72, color="#FFA300")
        self.add(sun)
        self.play(FadeIn(sun), duration=1.0)
        
        self.play_voiceover(
            "Einstein made a radical realization. Gravity isn't just a mysterious pulling force across a flat background.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "Massive objects like stars and black holes actually WARP the fabric of spacetime itself. "
            "Which means, the universe we live in is fundamentally Non-Euclidean!",
            voice="am_adam"
        )
        
        # Warp the grid visually by shifting some lines or using a particle effect
        self.play_sound(SoundFX.explosion())
        self.camera.shake(intensity=3, duration=1.5)
        self.wait(1.5)
        
        self.play_voiceover(
            "When light from a distant star travels past the Sun, the light isn't bending its path. "
            "The light is actually traveling in a perfectly straight line, but the spacetime canvas it is traveling on is severely curved.",
            voice="am_adam"
        )
        
        photon = Circle(radius=3, x=0, y=20, color="#FFF1E8")
        self.add(photon)
        self.play(FadeIn(photon), duration=0.5)
        
        # Manually create a curved trajectory
        sfx, dur = VoiceOver.generate("This is called a geodesic, the straightest possible path in a curved space.")
        
        # Animate photon curving around the sun
        self.play(MoveTo(photon, x=100, y=40), duration=dur/3)
        self.play(MoveTo(photon, x=128, y=38), duration=dur/3, sound=sfx)
        self.play(MoveTo(photon, x=256, y=20), duration=dur/3)
        
        self.play_voiceover(
            "This phenomenon, known as gravitational lensing, was exactly how astronomers proved Einstein's theory correct during a solar eclipse. "
            "They saw stars exactly where they mathematically shouldn't be, because the light followed the non-Euclidean curvature of our solar system.",
            voice="am_adam"
        )
        
        self.play(FadeOut(sun), FadeOut(photon), FadeOut(grid), FadeOut(bg), duration=1.5)

    def universe_shape_scene(self):
        bg = Rect(width=256, height=144, x=0, y=0, color="#000000")
        self.add(bg)
        self.play(FadeIn(bg), duration=1.0)
        
        self.play_voiceover(
            "But what about the BIG picture? If local space is warped by stars, what is the shape of the ENTIRE universe?",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "Cosmologists believe there are three main possibilities. "
            "If there is enough matter in the universe, it could have Positive Curvature, like a sphere. "
            "In this 'Closed Universe', if you travel far enough in one direction, you'd eventually end up back where you started.",
            voice="am_adam"
        )
        
        s1 = Circle(radius=30, x=128, y=72, color="#29ADFF", filled=False)
        self.add(s1)
        self.play(FadeIn(s1), duration=1.0)
        
        self.play_voiceover(
            "If there isn't enough matter, the universe could have Negative Curvature, like a saddle. "
            "In this 'Open Universe', parallel lines would diverge forever, and it would be infinite in extent.",
            voice="am_adam"
        )
        
        self.play(FadeOut(s1), duration=0.5)
        s2 = Rect(width=60, height=40, x=98, y=52, color="#FF004D", filled=False)
        self.add(s2)
        self.play(FadeIn(s2), duration=1.0)
        
        self.play_voiceover(
            "But here is the shocker. According to the latest data from the Planck satellite, our universe appears to be almost perfectly FLAT. "
            "Euclid's geometry, which we once thought was the absolute truth, then thought was a local approximation, "
            "actually seems to hold true for the universe on its grandest scale—within a margin of error of just zero point four percent.",
            voice="am_adam"
        )
        
        self.play_sound(SoundFX.powerup())
        flat_text = PixelText("FLAT UNIVERSE", x=128, y=110, align="center")
        self.add(flat_text)
        self.play(TypeWriter(flat_text), duration=1.0)
        
        self.play_voiceover(
            "Why is the universe so flat? This is one of the biggest mysteries in modern physics, leading to theories like 'Cosmic Inflation'. "
            "But the fact that we can even ask these questions shows how far Non-Euclidean geometry has pushed our imagination.",
            voice="am_adam"
        )
        
        self.play(FadeOut(s2), FadeOut(flat_text), FadeOut(bg), duration=1.0)

    def conclusion_scene(self):
        bg = Rect(width=256, height=144, x=0, y=0, color="#000000")
        self.add(bg)
        self.play(FadeIn(bg), duration=1.0)
        
        self.play_voiceover(
            "So, is the geometry you learned in school a lie? "
            "Not exactly.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "On a local, human scale, like building a house or designing a bridge, Euclidean geometry is remarkably accurate.",
            voice="am_adam"
        )
        
        house = Rect(width=40, height=40, x=108, y=70, color="#FF004D")
        roof = Rect(width=50, height=20, x=103, y=50, color="#00E436")
        self.add(house, roof)
        self.play(FadeIn(house), FadeIn(roof), duration=1.0)
        self.wait(1.0)
        
        self.play_voiceover(
            "But the moment we look at grand cosmic scales of relativity, or the deep quantum fabric of the universe, "
            "the flat paper is ripped apart.",
            voice="am_adam"
        )
        
        self.play(FadeOut(house), FadeOut(roof), duration=0.5)
        
        final_text = PixelText("THE UNIVERSE", x=128, y=50, align="center", color="#29ADFF")
        final_text2 = PixelText("IS CURVED", x=128, y=70, align="center", color="#FFCCAA")
        self.add(final_text, final_text2)
        
        self.play_sound(SoundFX.powerup())
        self.play(TypeWriter(final_text), duration=1.5)
        self.play(TypeWriter(final_text2), duration=1.5)
        
        self.play_voiceover(
            "Non-Euclidean geometry taught humanity our most valuable lesson: "
            "Never assume that your intuition about reality is the ultimate truth.",
            voice="am_adam"
        )
        
        self.play_voiceover(
            "We must follow the math, even when it curves into the unknown. "
            "Thank you for watching.",
            voice="am_adam"
        )
        
        self.wait(2.0)
        self.play(FadeOut(final_text), FadeOut(final_text2), duration=2.0)

if __name__ == "__main__":
    config = PixelConfig.landscape()
    scene = NonEuclideanGeometry(config)
    scene.render("non_euclidean_geom.mp4")
