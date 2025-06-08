import pandas as pd
import os
from dotenv import load_dotenv
import json
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from textwrap import wrap

# Load environment variables
load_dotenv()

api_key = os.getenv("api_key")
endpoint = os.getenv("url")
deployment_name = os.getenv("deployment_name")


def load_resource_data() -> str:
    try:
        # Load files
        df_demand = pd.read_csv("Demand_Forecast.csv")
        df_employee = pd.read_excel("EmployeeAllocationPlan.xlsx")
        df_machine = pd.read_excel("MachineProductionPlan.xlsx")

        # Convert timestamps to strings
        def convert_timestamps(df):
            for col in df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
                df[col] = df[col].astype(str)
            return df

        df_demand = convert_timestamps(df_demand)
        df_employee = convert_timestamps(df_employee)
        df_machine = convert_timestamps(df_machine)

        # Combine data
        data = {
            "DemandForecast": df_demand.to_dict(orient="records"),
            "EmployeeAllocation": df_employee.to_dict(orient="records"),
            "MachineProduction": df_machine.to_dict(orient="records")
        }

        return json.dumps(data)

    except Exception as e:
        return f"Error loading files: {str(e)}"


def save_text_to_pdf(text: str, filename: str = "report_output.pdf") -> str:
    try:
        # Create PDF with A4 size
        c = canvas.Canvas(filename, pagesize=A4)
        width, height = A4

        # Add heading
        heading = "Weekly Production and Workforce Planning Summary"
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 40, heading)

        # Set font for body text
        c.setFont("Courier", 10)

        # Starting Y position for the content
        y_position = height - 70
        max_chars_per_line = 100

        # Split text by lines
        for paragraph_line in text.splitlines():
            wrapped_lines = wrap(paragraph_line, width=max_chars_per_line) or [""]
            for line in wrapped_lines:
                c.drawString(40, y_position, line)
                y_position -= 15
                if y_position < 50:
                    c.showPage()
                    c.setFont("Helvetica-Bold", 16)
                    c.drawCentredString(width / 2, height - 40, heading)
                    c.setFont("Courier", 10)
                    y_position = height - 70

        c.save()
        return f"PDF successfully saved as: {filename}"
    except Exception as e:
        return f"Error generating PDF: {str(e)}"
