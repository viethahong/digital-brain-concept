# Digital Brain Concept

This is a template for a "Second Brain" system built with HTML, CSS, JavaScript, and Python. It's designed to help you manage your knowledge, principles, philosophies, and relationships through a structured wiki and an interactive dashboard.

## Features

- **Knowledge Graph**: Visualize the connections between your notes.
- **Progress Tracking**: Monitor your mastery levels (Biet, Hieu, Hanh, Thong, Tue) across different categories.
- **Brain Room**: An interactive command center that identifies gaps in your knowledge and provides prompts for growth.
- **Markdown-based**: Your notes are stored as simple `.md` files, ensuring they stay yours forever.

## Getting Started

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-username/digital-brain-concept.git
    cd digital-brain-concept
    ```

2.  **Add your notes**: Place your `.md` files in the corresponding folders within the `wiki/` directory. Use the following frontmatter at the top of each file:
    ```markdown
    ---
    title: Your Topic Name
    level: 1_Biet
    ---
    ```
    Available levels: `1_Biet`, `2_Hieu`, `3_Hanh`, `4_Thong`, `5_Tue`. (For relationships: `1_Biet`, `2_Quen`, `3_Than`, `4_Thuong`, `5_Yeu`).

3.  **Sync your brain**: Run the Python script to update the dashboard data:
    ```bash
    python3 brain_sync.py
    python3 brain_analyzer.py
    ```

4.  **Open the dashboard**: Simply open `index.html` in your web browser.

## Customization

- Modify `index.css` to change the look and feel.
- Update `prompts.html` to add your own exploration questions.

## License

This project is open-source. Feel free to use and modify it for your own personal growth.
