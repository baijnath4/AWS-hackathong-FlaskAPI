from flask import Flask, request, jsonify,send_from_directory, url_for
from forecastingagent import generate_forecast
from optimization import optimize_production
from crisisAgent import filter_by_date, send_email
from reportingAgent import load_resource_data, save_text_to_pdf
import json 
import os

app = Flask(__name__)

# Directory to store generated PDFs
UPLOAD_FOLDER = "generated_pdfs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return "Flask App for Forecasting, Optimization, Reporting, and Crisis Handling"

# Forecasting endpoint
@app.route("/api/forecast", methods=["GET"])
def forecast():
    try:
        df = generate_forecast()
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Optimization endpoint
@app.route("/api/optimize", methods=["GET"])
def optimize():
    try:
        machine, employee = optimize_production()
        return jsonify({
            "machine": machine.to_dict(orient="records"),
            "employee": employee.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Reporting: Load resource data
@app.route("/api/report/reportsummary", methods=["GET"])
def load_report_data():
    try:
        data_json = load_resource_data()
        return jsonify(json.loads(data_json)) if data_json.startswith("{") else jsonify({"error": data_json})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Reporting: Save PDF from given text
@app.route("/api/report/createPDF", methods=["POST"])
def save_report_pdf():
    try:
        req_data = request.get_json()
        text = req_data.get("text")
        filename = req_data.get("filename", "report_output.pdf")

        if not text:
            return jsonify({"error": "Missing 'text' in request"}), 400

        filepath = os.path.join(UPLOAD_FOLDER, filename)
        status = save_text_to_pdf(text, filepath)

        # Construct absolute URL
        pdf_url = request.host_url.rstrip("/") + url_for("view_pdf", filename=filename)

        return jsonify({
            "message": status,
            "pdf_url": pdf_url
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Reporting: View PDF
@app.route("/api/report/viewPDF/<filename>", methods=["GET"])
def view_pdf(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename, mimetype="application/pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 404
    
    
# Crisis: Filter by date
# @app.route("/api/crisis/filter", methods=["GET"])
# def crisis_filter():
#     target_date = request.args.get("date")
#     if not target_date:
#         return jsonify({"error": "Missing 'date' parameter"}), 400
#     records = filter_by_date(target_date)
#     return jsonify(records)

@app.route('/api/crisis/filter', methods=['POST'])
def filter_crisis():
    try:
        data = request.get_json(force=True)
        print(">>> Received data:", data)

        date = data.get('date')
        if not date:
            print(">>> Missing 'date' key in request")
            return jsonify({"error": "Missing date"}), 400

        records = filter_by_date(date)
        print(">>> Filtered records:", records)

        return jsonify({
            "status": "ok",
            "received_date": date,
            "records": records
        })

    except Exception as e:
        print(">>> Error in /api/crisis/filter:", str(e))
        return jsonify({"error": str(e)}), 500



# Crisis: Send email
@app.route("/api/crisis/email", methods=["POST"])
def crisis_email():
    try:
        req_data = request.get_json()
        subject = req_data.get("subject")
        recipient = req_data.get("recipient")
        body = req_data.get("body")

        if not all([subject, recipient, body]):
            return jsonify({"error": "Missing one or more required fields: subject, recipient, body"}), 400

        status = send_email(subject, recipient, body)
        return jsonify({"message": status})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501, debug=True)

