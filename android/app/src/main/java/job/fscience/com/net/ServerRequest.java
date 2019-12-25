package job.fscience.com.net;

import android.content.Context;
import android.text.TextUtils;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.cookie.CookieJarImpl;
import job.fscience.com.cookie.PersistentCookieStore;
import job.fscience.com.lib.MacUtils;
import okhttp3.*;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class ServerRequest {
    OkHttpClient client = null;

    String userId;
//    String baseUrl = "http://10.253.102.125:8002";
//    String baseUrl = "http://192.168.0.102:8002";
    String baseUrl = "http://212.64.26.210";
//    String baseUrl = "http://39.97.237.240";

    public ServerRequest(Context context) {
        client = new OkHttpClient.Builder()
                .cookieJar(new CookieJarImpl(new PersistentCookieStore(context))).build();
        userId = MacUtils.getMobileMAC(context);
    }

//    public void run(String url, Callback callback) throws IOException {
//        Request request = new Request.Builder().url(url).build();
//        client.newCall(request).enqueue(callback);
//    }

    public static String md5(String string) {
        if (TextUtils.isEmpty(string)) {
            return "";
        }
        MessageDigest md5 = null;
        try {
            md5 = MessageDigest.getInstance("MD5");
            byte[] bytes = md5.digest(string.getBytes());
            String result = "";
            for (byte b : bytes) {
                String temp = Integer.toHexString(b & 0xff);
                if (temp.length() == 1) {
                    temp = "0" + temp;
                }
                result += temp;
            }
            return result;
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
        }
        return "";
    }

    public void checkLogin(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/admin/login").build();
        client.newCall(request).enqueue(callback);
    }

    public void managerLogin(String userName, String password, Callback callback) {
        RequestBody body = new FormBody.Builder().add("username", userName.trim()).add("password", md5(password.trim())).build();
        Request request = new Request.Builder().url(baseUrl + "/api/admin/login").post(body).build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetExam(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/exam").build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetExamUsers(int examId, Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/admin/examuser/list/" + examId).build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetLocations(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/locations").build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetUserTrack(int userId, long startTime, long endTime, Callback callback) {
        String params = "?start=" + startTime + "&end=" + endTime;
        Request request = new Request.Builder().url(baseUrl + "/api/manager/track/" + userId + params).build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetResult(int userId, Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/user/result/" + userId).build();
        client.newCall(request).enqueue(callback);
    }

    public void managerGetResults(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/user/results").build();
        client.newCall(request).enqueue(callback);
    }

    public void managerQueryResults(double level1, double level2, double level3, double level4, Callback callback) {
        RequestBody body = new FormBody.Builder()
                .add("level1", "" +level1)
                .add("level2", "" + level2)
                .add("level3", "" + level3)
                .add("level4", "" + level4)
                .build();
        Request request = new Request.Builder().url(baseUrl + "/api/manager/user/results").post(body).build();
        client.newCall(request).enqueue(callback);
    }

    public void getExams(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/manager/exams").build();
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
