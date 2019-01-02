package job.fscience.com.net;

import android.content.Context;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.lib.MacUtils;
import okhttp3.*;

public class ServerRequest {
    OkHttpClient client = new OkHttpClient();

    String userId;
    String baseUrl = "http://10.253.102.55";
//    String baseUrl = "http://212.64.26.210";

    public ServerRequest(Context context) {
        userId = MacUtils.getMobileMAC(context);
    }

    public void checkLogin(String deviceId, Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/user/autologin?device_id=" + deviceId).build();
        client.newCall(request).enqueue(callback);
    }

    public void userLogin(String deviceId, String lineId, String userName, String departName, Callback callback) {
        RequestBody body = new FormBody.Builder()
                .add("device_id", deviceId)
                .add("line_id", "" + lineId)
                .add("username", "" + userName)
                .add("departname", "" + departName).build();

        Request request = new Request.Builder().url(baseUrl + "/api/user/autologin").post(body).build();
        client.newCall(request).enqueue(callback);
    }

    public void userLines(Callback callback) {
        Request request = new Request.Builder().url(baseUrl + "/api/admin/examline/list").build();
        client.newCall(request).enqueue(callback);
    }

    public void userUploadPosition(int userId, double latitude, double longitude, int manual, Callback callback) {
        RequestBody body = new FormBody.Builder()
                .add("latitude", "" + latitude)
                .add("longitude", "" + longitude)
                .add("manual", "" + manual)
                .add("user_id", "" + userId).build();

        Request request = new Request.Builder().url(baseUrl + "/api/user/position").post(body).build();
        client.newCall(request).enqueue(callback);
    }


    public static JSONObject parseJSON(Response response) {
        try {
            return JSON.parseObject(response.body().string());
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}
