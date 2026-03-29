from pixelengine import CleanScene, PixelConfig, VStack, PixelText, Rect

class MinimalVideo(CleanScene):
    def construct(self):
        # High resolution canvas doesn't need heavy scanlines or glitch FX to look good.
        # It relies on crisp geometry and typography.
        self.set_background("#EAEAEA") # Soft white background
        
        # We are using 540x960 (high_res_portrait). Center is 270x480.
        logo = Rect(width=80, height=80, color="#FF004D")
        
        main_text = PixelText("CLEAN ART", scale=4, color="#1D2B53")
        sub_text  = PixelText("High Definition . Smooth . Minimal", scale=1, color="#83769C")
        
        # Declaratively stack them! No math needed.
        layout = VStack([logo, main_text, sub_text], spacing=30, align="center")
        
        # Push the stack to the absolute center of the 540x960 canvas
        layout.move_to(270, 480)
        self.add(layout)
        
        # Our custom macro handles the floating organic reveal and piano arpeggios
        self.play_clean_reveal(layout, duration=2.5)
        
        self.wait(1.5)

if __name__ == "__main__":
    # Activate high definition output here! (Canvas: 540x960 -> Output: 1080x1920)
    MinimalVideo(PixelConfig.high_res_portrait()).render()
