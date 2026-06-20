using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using System.Collections;
using System.Text;

[System.Serializable]
public class MensajeChat { public string texto; }

[System.Serializable]
public class RespuestaServidor 
{ 
    public string status; 
    public string respuesta; // <-- AGREGADO: Para capturar el texto que genera Gemini
    public string archivo; 
    public string mensaje; 
}

public class ChatClient : MonoBehaviour
{
    [Header("Componentes de Interfaz")]
    public TMP_InputField inputField;
    public TMP_Text textoRespuestaUI; // <-- AGREGADO: Arrastra aquí el cuadro de texto donde hablará el Chamán
    
    [Header("Control de Personaje")]
    public AvatarController avatarController;
    
    [Header("Configuración de Red")]
    public string url = "http://127.0.0.1:8000/chat";

    public void EnviarDatos()
    {
        if (string.IsNullOrEmpty(inputField.text)) return;
        StartCoroutine(ComunicarConPython(inputField.text));
    }

    IEnumerator ComunicarConPython(string mensajeUsuario)
    {
        // Feedback visual mientras el Chamán piensa
        if (textoRespuestaUI != null) textoRespuestaUI.text = "Sulkía consulta los registros sagrados de Kabré...";

        MensajeChat objetoJSON = new MensajeChat { texto = mensajeUsuario };
        string json = JsonUtility.ToJson(objetoJSON);
        byte[] bodyRaw = Encoding.UTF8.GetBytes(json);

        using (UnityWebRequest request = new UnityWebRequest(url, "POST"))
        {
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");
            
            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.ConnectionError || request.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.LogError("Error de conexión con el servidor: " + request.error);
                if (textoRespuestaUI != null) textoRespuestaUI.text = "Error de conexión con el Oráculo.";
            }
            else
            {
                string respuestaJson = request.downloadHandler.text;
                Debug.Log("RESPUESTA CRUDA DEL SERVIDOR: " + respuestaJson);

                RespuestaServidor data = JsonUtility.FromJson<RespuestaServidor>(respuestaJson);

                if (data.status == "success")
                {
                    // 1. CORRECCIÓN: Mostramos el texto en la interfaz de Unity
                    if (textoRespuestaUI != null) 
                    {
                        textoRespuestaUI.text = data.respuesta;
                    }

                    // Limpiamos el cuadro de entrada para la siguiente pregunta
                    inputField.text = "";

                    // 2. Tu lógica original: Mandar el audio al AvatarController
                    if (!string.IsNullOrEmpty(data.archivo))
                    {
                        Debug.Log("URL de audio recibida correctamente: " + data.archivo);
                        avatarController.PlayResponse(data.archivo);
                    }
                }
                else
                {
                    Debug.LogError("El servidor Python reportó un error: " + data.mensaje);
                    if (textoRespuestaUI != null) textoRespuestaUI.text = "Error: " + data.mensaje;
                }
            }
        }
    }
}
