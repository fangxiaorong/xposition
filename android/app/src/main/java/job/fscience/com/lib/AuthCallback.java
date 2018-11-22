package job.fscience.com.lib;

import android.app.Activity;
import android.content.Intent;
import android.widget.Toast;
import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import job.fscience.com.xposition.LoginActivity;
import job.fscience.com.xposition.XApplication;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.Response;

import java.io.IOException;

public abstract class AuthCallback implements Callback {

    @Override
    public final void onFailure(Call call, IOException e) {
        this.onFailureEx(call, e);
    }

    @Override
    public final void onResponse(Call call, Response response) throws IOException {
        JSONObject data = null;
        try {
            data = JSON.parseObject(response.body().string());
        } catch (Exception e) {}

        if (data != null && data.getInteger("state") == 2000) {
            Activity activeActivity = XApplication.getActiveActivity();
            if (!activeActivity.getClass().getSimpleName().equals("LoginActivity")) {
                Intent intent = new Intent(activeActivity, LoginActivity.class);
                activeActivity.startActivity(intent);
            } else {
                final Activity tmpActivity = activeActivity;
                final JSONObject tmpData = data;
                activeActivity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(tmpActivity, tmpData.getString("message"), Toast.LENGTH_SHORT).show();
                    }
                });
            }
        } else {
            this.onResponseEx(data);
        }
    }

    public abstract void onFailureEx(Call call, IOException e);
    public abstract void onResponseEx(JSONObject data) throws IOException;
}
