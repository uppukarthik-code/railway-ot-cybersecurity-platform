def generate_html_report(

    findings,

    output_file="outputs/validation_report.html"
):

    from collections import Counter
    from datetime import datetime

    counts = Counter()

    for f in findings:

        counts[
            f["severity"]
        ] += 1

    html = f"""

    <html>

    <head>

        <title>
            Railway OT Cybersecurity Assessment
        </title>

        <style>

            body {{

                font-family: Arial;
                margin: 40px;
                background: #f4f6f8;
            }}

            h1 {{

                color: #222;
            }}

            .summary {{

                display: flex;
                gap: 20px;
                margin-bottom: 30px;
            }}

            .card {{

                background: white;
                padding: 20px;
                border-radius: 8px;
                width: 180px;
                text-align: center;
                box-shadow: 0px 2px 6px rgba(0,0,0,0.1);
            }}

            .critical {{
                border-top: 6px solid #ff4d4d;
            }}

            .high {{
                border-top: 6px solid #ff944d;
            }}

            .medium {{
                border-top: 6px solid #ffd24d;
            }}

            .low {{
                border-top: 6px solid #70db70;
            }}

            .finding {{

                background: white;
                padding: 20px;
                margin-bottom: 16px;
                border-radius: 8px;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.08);
            }}

            .severity {{

                font-weight: bold;
                margin-bottom: 10px;
            }}

        </style>

    </head>

    <body>

        <h1>
            Railway OT Cybersecurity Validation Report
        </h1>

        <p>
            Generated:
            {datetime.now()}
        </p>

        <div class="summary">

            <div class="card critical">

                <h2>
                    {counts.get('CRITICAL',0)}
                </h2>

                <p>Critical</p>

            </div>

            <div class="card high">

                <h2>
                    {counts.get('HIGH',0)}
                </h2>

                <p>High</p>

            </div>

            <div class="card medium">

                <h2>
                    {counts.get('MEDIUM',0)}
                </h2>

                <p>Medium</p>

            </div>

            <div class="card low">

                <h2>
                    {counts.get('LOW',0)}
                </h2>

                <p>Low</p>

            </div>

        </div>

    """

    for f in findings:

        severity = f.get(
            "severity",
            "LOW"
        )

        html += f"""

        <div class="finding">

            <h3>
                {f.get('type')}
            </h3>

            <div class="severity">

                Severity:
                {severity}

            </div>

            <p>
                {f.get('message')}
            </p>

            <p>

                <b>Recommendation:</b>

                {f.get('recommendation')}

            </p>

        </div>

        """

    html += """

    </body>
    </html>

    """

    with open(

        output_file,

        "w",

        encoding="utf-8"

    ) as fp:

        fp.write(html)

    print(
        f"[OK] HTML report generated: {output_file}"
    )