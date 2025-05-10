from flask import Flask, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/solar_cep/<string:cep>/<float:peakpower>', methods=['GET'])
def get_solar_data_from_cep(cep, peakpower):
    # Passo 1: CEP pra endereço
    viacep_url = f"https://viacep.com.br/ws/{cep}/json/"
    viacep_response = requests.get(viacep_url)
    if viacep_response.status_code != 200 or "erro" in viacep_response.json():
        return jsonify({"error": "CEP inválido"}), 400
    
    endereco = viacep_response.json()
    full_address = f"{endereco['logradouro']}, {endereco['bairro']}, {endereco['localidade']}, {endereco['uf']}, Brasil"

    # Passo 2: Endereço pra coordenadas
    nominatim_url = f"https://nominatim.openstreetmap.org/search?q={full_address}&format=json"
    headers = {"User-Agent": "SolarAPI/1.0"}
    nominatim_response = requests.get(nominatim_url, headers=headers)
    if nominatim_response.status_code != 200 or not nominatim_response.json():
        return jsonify({"error": "Falha ao geocodificar"}), 500
    
    coords = nominatim_response.json()[0]
    lat, lon = coords["lat"], coords["lon"]

    # Passo 3: Coordenadas pro PVGIS
    pvgis_url = f"https://re.jrc.ec.europa.eu/api/v5_2/PVcalc?lat={lat}&lon={lon}&outputformat=json&raddatabase=PVGIS-SARAH2&peakpower={peakpower}&loss=14"
    pvgis_response = requests.get(pvgis_url)
    if pvgis_response.status_code == 200:
        data = pvgis_response.json()
        totals = data["outputs"]["totals"]["fixed"]
        return jsonify({
            "cep": cep,
            "endereco": full_address,
            "latitude": float(lat),
            "longitude": float(lon),
            "irradicao_diaria_kwh_m2": totals["H(i)_d"],
            "energia_diaria_kwh": totals["E_d"],
            "energia_anual_kwh": totals["E_y"]
        })
    else:
        return jsonify({"error": "Falha no PVGIS"}), pvgis_response.status_code

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)