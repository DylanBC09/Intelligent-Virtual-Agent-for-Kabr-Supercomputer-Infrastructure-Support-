using UnityEngine;
using UnityEngine.Networking;
using TMPro;
using System.Collections;
using System.Text;

// Clase para enviar datos al servidor
[System.Serializable]
public class MensajeChat 
{ 
    public string user_id; 
    public string texto; 
}

// Clase para recibir datos del servidor (Debe coincidir con main.py)
[System.Serializable]
public class RespuestaServidor 
{ 
    public string respuesta; 
    public string url_audio; 
}

public class ChatClient : MonoBehaviour
{
    [Header("Componentes de Interfaz")]
    public TMP_InputField inputField;
    public TMP_Text textoRespuestaUI;
    
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
        if (textoRespuestaUI != null) textoRespuestaUI.text = "Sulkía consulta los registros sagrados de Kabré...";

        // Creamos el objeto JSON con user_id y texto
        MensajeChat objetoJSON = new MensajeChat { 
            user_id = "usuario_01", 
            texto = mensajeUsuario 
        };
        
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
                Debug.LogError("Error de conexión: " + request.error);
                if (textoRespuestaUI != null) textoRespuestaUI.text = "Error de conexión con el Oráculo.";
            }
            else
            {
                string respuestaJson = request.downloadHandler.text;
                Debug.Log("RESPUESTA RECIBIDA: " + respuestaJson);

                RespuestaServidor data = JsonUtility.FromJson<RespuestaServidor>(respuestaJson);

                if (data != null && !string.IsNullOrEmpty(data.respuesta))
                {
                    // Mostrar texto en UI
                    if (textoRespuestaUI != null) textoRespuestaUI.text = data.respuesta;

                    inputField.text = "";

                    // Mandar audio al AvatarController
                    if (!string.IsNullOrEmpty(data.url_audio))
                    {
                                               Debug.Log("Reproduciendo audio desde: " + data.url_audio);
                        avatarController.PlayResponse(data.url_audio);
                    }
                }
                else
                {
                    Debug.LogError("El servidor devolvió un formato inesperado.");
                }
            }
        }
    }
}
