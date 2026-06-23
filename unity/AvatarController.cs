using UnityEngine;
using UnityEngine.Networking;
using System.Collections;

public class AvatarController : MonoBehaviour
{
    [Header("Configuración del Personaje")]
    // Arrastra aquí el objeto de la jerarquía que tiene el SkinnedMeshRenderer de la cara
    public SkinnedMeshRenderer mallaCara; 
    
    // Escribe el nombre EXACTO del shape key para abrir la boca (ej. "Mouth_Open", "Jaw_Open", "Boca")
    public string nombreShapeKey = "Clave 1"; 

    [Header("Ajustes de Movimiento")]
    [Range(100f, 2000f)] public float sensibilidad = 500f; // Qué tanto abre la boca con el volumen
    public float maximoApertura = 100f; // El límite del Blend Shape (usualmente 100)

    private AudioSource audioSource;
    private int indexShapeKey = -1;
    
    // Almacenamos el array aquí para no crear basura en memoria cada frame
    private float[] datosAudio = new float[256];

    void Awake()
    {
        audioSource = GetComponent<AudioSource>();
        if (audioSource == null)
        {
            audioSource = gameObject.AddComponent<AudioSource>();
        }
    }

    void Start()
    {
        if (mallaCara != null)
        {
            // Buscamos el índice interno del shape key por su nombre
            indexShapeKey = mallaCara.sharedMesh.GetBlendShapeIndex(nombreShapeKey);
            if (indexShapeKey == -1)
            {
                Debug.LogError($"[Avatar] No se encontró ningún Shape Key llamado '{nombreShapeKey}' en la malla configurada.");
            }
        }
        else
        {
            Debug.LogError("[Avatar] Por favor, asigna la 'Malla Cara' en el Inspector de Unity.");
        }
    }

    // LateUpdate se ejecuta después del Animator, asegurando que el script tenga la última palabra
    void LateUpdate()
    {
        // Si no hay malla o no se encontró el Shape Key, no hacemos nada
        if (mallaCara == null || indexShapeKey == -1) return;

        // CONDICIÓN CLAVE: ¿El audio existe y realmente está sonando?
        if (audioSource != null && audioSource.isPlaying)
        {
            // Obtenemos los datos de salida del audio actual
            audioSource.GetOutputData(datosAudio, 0);

            // Calculamos el volumen promedio (RMS) de la muestra actual
            float suma = 0f;
            for (int i = 0; i < datosAudio.Length; i++)
            {
                suma += Mathf.Abs(datosAudio[i]);
            }
            float volumenPromedio = suma / datosAudio.Length;

            // Calculamos el peso final multiplicando por la sensibilidad
            float pesoBoca = Mathf.Clamp(volumenPromedio * sensibilidad, 0f, maximoApertura);

            // Aplicamos el movimiento al Shape Key de la boca
            mallaCara.SetBlendShapeWeight(indexShapeKey, pesoBoca);
        }
        else
        {
            // ¡BOCA CERRADA A LA FUERZA! Si no está hablando, el valor es 0 en cada frame.
            mallaCara.SetBlendShapeWeight(indexShapeKey, 0f);
        }
    }

    public void PlayResponse(string urlAudio)
    {
        if (string.IsNullOrEmpty(urlAudio)) return;
        StartCoroutine(DescargarYReproducir(urlAudio));
    }

    IEnumerator DescargarYReproducir(string url)
    {
        using (UnityWebRequest www = UnityWebRequestMultimedia.GetAudioClip(url, AudioType.MPEG))
        {
            yield return www.SendWebRequest();

            if (www.result == UnityWebRequest.Result.ConnectionError || www.result == UnityWebRequest.Result.ProtocolError)
            {
                Debug.LogError("Error descargando audio: " + www.error);
            }
            else
            {
                AudioClip clip = DownloadHandlerAudioClip.GetContent(www);
                audioSource.clip = clip;
                audioSource.Play();
                // Nota: Ya no iniciamos una coroutine aquí, LateUpdate se encarga de todo de forma automática
            }
        }
    }
}