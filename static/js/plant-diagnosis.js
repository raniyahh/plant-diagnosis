document.getElementById("diagnose-button").addEventListener("click", async function () {
  const fileInput = document.getElementById("plant-image");
  const file = fileInput.files[0];
  if (!file) return alert("الرجاء اختيار صورة.");

  const formData = new FormData();
  formData.append("image", file);

  const response = await fetch("/diagnose", {
    method: "POST",
    body: formData
  });

  const data = await response.json();
  const output = document.getElementById("result");

  const isHealthy = data.result?.is_healthy?.binary;
  const diseases = data.result?.disease?.suggestions || [];
  const symptoms = data.result?.symptom?.suggestions || [];

  let html = `<h4>🌿 حالة النبات: ${isHealthy === true ? "صحي ✅" : "مريض ⚠️"}</h4>`;

  const diseaseTranslations = {
    "Fungi": "فطريات",
    "Animalia": "حيوانات",
    "feeding damage by insects": "ضرر ناتج عن الحشرات",
    "nutrient deficiency": "نقص في العناصر الغذائية",
    "Colletotrichum": "الجمرة الخبيثة (فطر)",
    "Insecta": "حشرات",
    "Bacteria": "بكتيريا",
    "light excess": "زيادة الإضاءة"
  };
    
  if (diseases.length > 0) {
    html += "<h4>🦠 التشخيصات المحتملة:</h4><ul>";
 
    diseases.forEach(d => {
      const translatedName = diseaseTranslations[d.name] || d.name;
      html += `<li><strong>${translatedName} (${d.name})</strong> (احتمالية: ${(d.probability*100).toFixed(1)}%)</li>`;
    });
    html += "</ul>";
  }

  if (symptoms.length > 0) {
    html += "<h4>📌 الأعراض الملحوظة:</h4><ul>";
    symptoms.forEach(s => {
      html += `<li>${s.name} (احتمالية: ${(s.score*100).toFixed(1)}%)</li>`;
    });
    html += "</ul>";
  }

  output.innerHTML = html;
});
