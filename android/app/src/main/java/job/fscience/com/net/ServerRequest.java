package job.fscience.com.net;

import android.content.Context;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.MacUtils;
import okhttp3.*;

import java.io.IOException;

public class ServerRequest {
    OkHttpClient client = new OkHttpClient();

    String userId;
//    String baseUrl = "http://10.0.109.50:8002";
    String baseUrl = "http://212.64.26.210:8002";

    public ServerRequest(Context context) {
        userId = MacUtils.getMobileMAC(context);
    }

    public void run(String url, Callback callback) throws IOException {
        Request request = new Request.Builder().url(url).build();
        client.newCall(request).enqueue(callback);
    }

    public void managerLogin(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/login").build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetExam(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/exam").build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetLocations(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/locations").build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetUserTrack(int userId, Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/track/" + userId).build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetResult(int userId, Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/user/result/" + userId).build();
        client.newCall(request).enqueue(callback);
    }


    public static JSONObject parseJSON(Response response) {
        try {
            return JSON.parseObject(response.body().string());
        } catch (Exception e) {}
        return null;
    }

//    public void getExamLine(Callback callback) {
//        Request request = new Request.Builder().url(baseUrl + "/api/exam/line/" + userId).build();
//        client.newCall(request).enqueue(callback);
//    }
//
//    public void uploadPosition(double latitude, double longitude, Callback callback) {
//        try {
//            JSONObject object = new JSONObject();
//            object.put("latitude", latitude);
//            object.put("longitude", longitude);
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
