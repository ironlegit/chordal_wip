import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
import chordal_wip.scales as cw
from chordal_wip.notes import ALL_NOTES

class MyBoxLayout(BoxLayout):
    # Init infinte keywords
    def __init__(self, **kwargs):
        # Init BoxLayout parent class
        super(MyBoxLayout, self).__init__(**kwargs)

        # Stack drop down and chord grid vertically
        self.orientation = "vertical"

        # Drop down for chord type
        self.spinner_chord_type = Spinner(
            text="triads",  # default text
            values=("triads", "7ths"),  # Options
            size_hint=(0.2, 0.1),  # relative height and width,
            pos_hint={"center_x": 0.5},  # position param
        )

        # Call method when drop down is used
        self.spinner_chord_type.bind(text=self.on_spinner_select)

        # Add widget to layout
        self.add_widget(self.spinner_chord_type)

        # Add GridLayout for chords
        # TODO: Add logic to expand grid depending on n_chords
        self.grid = GridLayout(
            cols=2,  # n of columns
            spacing=[
                10,
                80,
            ],  # Add this line to increase vertical spacing between rows
            padding=10,  # Optional: Add padding around the grid (optional)
        )

        # Replace your chord_labels list creation with this:
        self.chord_displays = []
        for i in range(4):  # For 4 chords
            # Create a vertical layout for each chord
            chord_layout = BoxLayout(
                orientation="vertical",
                size_hint=(0.5, None),
                height=80,  # Fixed height for each chord display
                spacing=2,  # Space between lines
            )

            # Chord name label (big and bold)
            chord_name = Label(
                text=f"Chord_{i + 1}",
                font_size=24,
                bold=True,
                halign="center",
                valign="middle",
                size_hint=(1, 0.4),
            )

            # Roman numeral label (smaller)
            roman_numeral = Label(
                text="",
                font_size=18,
                halign="center",
                valign="middle",
                size_hint=(1, 0.3),
            )

            # Chord degree label (smallest, in parentheses)
            chord_degree = Label(
                text="",
                font_size=14,
                halign="center",
                valign="middle",
                size_hint=(1, 0.3),
            )

            # Add labels to the chord layout
            chord_layout.add_widget(chord_name)
            chord_layout.add_widget(roman_numeral)
            chord_layout.add_widget(chord_degree)

            # Add the chord layout to the grid and to our list
            self.grid.add_widget(chord_layout)
            self.chord_displays.append(
                {
                    "name": chord_name,
                    "roman": roman_numeral,
                    "degree": chord_degree,
                }
            )

        # Add the grid to the main layout
        self.add_widget(self.grid)

        self.spinner_root = Spinner(
            text="C",
            values=ALL_NOTES,  #
            size_hint=(0.2, 0.1),
        )
        self.add_widget(self.spinner_root)

        # Spinner
        self.spinner_mode = Spinner(
            text="ionian",
            values=list(cw.Scale.SCALES_DICT.keys()),  #
            size_hint=(0.2, 0.1),
        )
        self.add_widget(self.spinner_mode)

        self.generate_button = Button(
            text="Go",
            size_hint=(0.5, 0.1),  #
        )
        self.generate_button.bind(on_press=self.call_progression)
        self.add_widget(self.generate_button)

        # Add footnote at the bottom
        footnote_layout = BoxLayout(
            size_hint=(1, 0.05)
        )  # Full width, 5% height

        # Empty label to push footnote to the right
        footnote_layout.add_widget(Label(size_hint=(0.8, 1)))

        # Footnote label
        # TODO: Fix formatting
        footnote = Label(
            text="Powered by Robo [【•】◡【•】]",
            size_hint=(0.2, 1),
            halign="right",
            valign="middle",
            font_size=12,
            color=(0.5, 0.5, 0.5, 1),
        )
        footnote_layout.add_widget(footnote)

        # Add footnote layout to the main layout
        self.add_widget(footnote_layout)
        # TODO: Add all add_widgets here

        # Init progression
        self.progression = None
        self.call_progression(None)

    def call_progression(self, instance):
        """Generate a new chord progression based on current selections.

        Creates a new chord progression using the selected root note and mode,
        then updates the displayed chords.

        Args:
            instance: The button instance that triggered this method (unused).
        """
        # Get scale and chord
        root_note = self.spinner_root.text
        mode = self.spinner_mode.text
        scale = cw.Scale(root_note, mode)
        chord = cw.Chord(scale)

        # Create progression
        # TODO: Extract total tension, could be used as a metric
        progression = cw.MarkovChordProgression(n_chords=4, chord=chord)
        self.progression = progression.progression

        # Update ALL chord information (not just triads/7ths)
        self.update_chord_display()

    def update_chord_display(self):
        """
        Update the chord display with all information (name, roman numeral, degree).
        """
        if self.progression is None:
            return

        # Get the current chord type (triads or 7ths)
        chord_type = self.spinner_chord_type.text

        # Extract all data from the DataFrame
        chords = self.progression[chord_type].tolist()
        roman_numerals = self.progression["roman"].tolist()
        degrees = self.progression["name"].tolist()

        for i, display in enumerate(self.chord_displays):
            if i < len(chords):
                display["name"].text = chords[i]
                display["roman"].text = roman_numerals[i]
                display["degree"].text = f"({degrees[i]})"
            else:
                # Reset placeholders
                display["name"].text = f"Chord_{i + 1}"
                display["roman"].text = ""
                display["degree"].text = ""

    def on_spinner_select(self, spinner, text):
        """Update chord labels when the chord type spinner selection changes.

        Extracts the selected chord type (triads or 7ths) from the progression
        DataFrame and updates the displayed chord labels.

        Args:
            spinner: The spinner widget that triggered this method (unused).
            text: The selected value from the spinner ('triads' or '7ths').
        """
        # Check if p exists, else do nothing
        if self.progression is not None:
            chords = self.progression[text].tolist()  # Get triads or 7ths
            for i, display in enumerate(self.chord_displays):
                # handles not replacing place holders when n_chords < 4
                if i < len(chords):
                    display["name"].text = chords[i]


class MyApp(App):
    def build(self):
        return MyBoxLayout()


if __name__ == "__main__":
    MyApp().run()
