import requests
from config import RAIL_API


def fetch_pnr_details(pnr: str) -> str:
    base_url = "http://indianrailapi.com/api/v2/PNRCheck"
    url = f"{base_url}/apikey/{RAIL_API}/PNRNumber/{pnr}/"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Status") != "SUCCESS":
            return f"Failed to fetch PNR details: {data.get('Message', 'Unknown error')}"

        # Parse the response to a readable message
        msg_lines = [
            f"PNR Number: {data.get('PnrNumber')}",
            f"Train: {data.get('TrainNumber')} - {data.get('TrainName')}",
            f"From: {data.get('From')}  To: {data.get('To')}",
            f"Journey Date: {data.get('JourneyDate')}",
            f"Class: {data.get('JourneyClass')}",
            "Passenger Statuses:"
        ]

        passengers = data.get("Passangers", [])
        for p in passengers:
            msg_lines.append(
                f"{p.get('Passenger')}: Booking - {p.get('BookingStatus')}, Current - {p.get('CurrentStatus')}"
            )

        return "\n".join(msg_lines)

    except requests.RequestException as e:
        return f"Error fetching PNR details: {e}"

if __name__ == "__main__":
    fetch_pnr_details(pnr="4318406150")