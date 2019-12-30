package job.fscience.com.xposition;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import job.fscience.com.lib.BaseActivity;

public class SettingsActivity extends BaseActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_settings);

        findViewById(R.id.app_download).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(SettingsActivity.this, AppDownloadActivity.class);
                startActivity(intent);
            }
        });
        findViewById(R.id.exam_lines).setVisibility(View.INVISIBLE);
        findViewById(R.id.exam_lines).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                Intent intent = new Intent(SettingsActivity.this, LineListActivity.class);
                startActivity(intent);
            }
        });
    }
}
