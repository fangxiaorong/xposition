package job.fscience.com.net;

import android.content.Context;
import job.fscience.com.lib.MacUtils;
import okhttp3.*;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;

public class ServerRequest {
    OkHttpClient client = new OkHttpClient();

    String userId;
//    String baseUrl = "http://10.0.109.50:8002";
//    String baseUrl = "http://212.64.26.210:8002";
    String baseUrl = "http://192.168.48.95:8002";

    public ServerRequest(Context context) {
        userId = MacUtils.getMobileMAC(context);
    }

    public void userLogin(String deviceId, Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/user/login/" + deviceId).build();
        client.newCall(request).enqueue(callback);
    }

    public void userUploadPosition(int userId, double latitude, double longitude, int type, Callback callback) {
        try {
            JSONObject object = new JSONObject();
            object.put("latitude", latitude);
            object.put("longitude", longitude);
            object.put("type", type);
            object.put("user_id", userId);
            RequestBody body = RequestBody.create(MediaType.parse(""), object.toString());

            Request request = new Request.Builder().url(baseUrl + "/api/user/position").build();
            client.newCall(request).equals(callback);
        } catch (JSONException e) {}
    }

//    public void run(String url, Callback callback) throws IOException {
//        Request request = new Request.Builder().url(url).build();
//        client.newCall(request).enqueue(callback);
//    }
//
//    public void getExamLine(Callback callback) {
//        Request request = new Request.Builder().url(baseUrl + "/api/exam/line/" + userId).build();
//        client.newCall(request).enqueue(callback);
//    }
//
//    public void uploadPosition(double latitude, double longitude, int type, Callback callback) {
//        try {
//            JSONObject object = new JSONObject();
//            object.put("latitude", latitude);
//            object.put("longitude", longitude);
//            object.put("type", type);
//            object.put("mac", userId);
//            RequestBody body = RequestBody.create(MediaType.parse(""), object.toString());
//            Request request = new Request.Builder().url(baseUrl + "/api/upload/position").post(body).build();
//            client.newCall(request).enqueue(callback);
//        } catch (JSONException ex) {
//            ex.printStackTrace();
//        }
//    }
//
//    public void getExamUser(Callback callback) {
//        Request request = new Request.Builder().url(baseUrl + "/api/exam/users").build();
//        client.newCall(request).enqueue(callback);
//    }
//
//    public void getExamUsersPos(int examId, Callback callback) {
//        Request request = new Request.Builder().url(baseUrl + "/api/exam/userspos/" + examId).build();
//        client.newCall(request).enqueue(callback);
//    }
//
//    public void getExamUserPos(int userId, Callback callback) {
//        Request request = new Request.Builder().url(baseUrl + "/api/exam/user/pos/" + userId).build();
//        client.newCall(request).enqueue(callback);
//    }
//
//    public void getExamResult(int userId, Callback callback) {
//        Request request = new Request.Builder().url(baseUrl + "/api/exam/result/" + userId).build();
//        client.newCall(request).enqueue(callback);
//    }
}
