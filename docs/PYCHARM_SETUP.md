# Open and run in PyCharm

1. Extract the ZIP into its own directory.
2. In PyCharm, choose **Open** and select the directory containing this file.
3. Use Python 3.11 or newer for the project interpreter. A fresh virtual
   environment is recommended.
4. Open PyCharm's Terminal and run:

   ```bash
   python -m pip install -e ".[dev]"
   ```

5. Run the demonstration:

   ```bash
   python -m graids_demo
   ```

6. Run the tests:

   ```bash
   python -m pytest -q
   ```

The sample does not require a Discord token or `.env` file.

## Uploading to GitHub

The cleanest approach is to create a **new** GitHub repository rather than
importing any historical project directory:

```bash
git init
git add .
git status
git commit -m "Initial public GRAIDS source demo"
git branch -M main
git remote add origin <YOUR_NEW_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Before the `git commit`, inspect `git status` and confirm there are no `.env`,
database, log, archive, or unrelated files. Do not copy the original production
folder into this public repository after initialization.
