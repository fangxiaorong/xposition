package job.fscience.com.lib;

import android.support.v7.app.AppCompatActivity;
import job.fscience.com.xposition.XApplication;

public class BaseActivity extends AppCompatActivity {
    @Override
    protected void onResume() {
        super.onResume();
        XApplication.setActiveActivity(this);
    }
}
