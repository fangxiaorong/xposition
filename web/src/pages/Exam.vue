<template>
  <div>
    <v-container grid-list-xl fluid>
      <v-layout row wrap>
        <v-flex lg3>
          <v-card>
            <v-list>
              <v-list-tile v-for="item in exams" :key="item.id" @click="pathSelected(item)">
                <v-list-tile-action>
                  <v-btn icon ripple @click.stop="examActive(item)">
                    <v-icon color="primary">{{ item.id === active_exam_id ? 'lock' : (item.state === 2 ? 'history' : 'lock_open') }}</v-icon>
                  </v-btn>
                </v-list-tile-action>

                <v-list-tile-content>
                  <v-list-tile-title v-text="item.name"></v-list-tile-title>
                </v-list-tile-content>

                <v-list-tile-avatar v-if="item.state === 1">
                  <v-btn icon ripple @click.stop="editExam(item)">
                    <v-icon color="grey lighten-1">edit</v-icon>
                  </v-btn>
                </v-list-tile-avatar>

              </v-list-tile>
              <v-dialog v-model="examDialog" max-width="800px">
                <v-btn slot="activator" color="primary" dark class="mb-2">新增</v-btn>
                <v-card>
                  <v-card-title>
                    <span class="headline">新建考试</span>
                  </v-card-title>
                  <v-card-text>
                    <v-container grid-list-md>
                      <v-layout wrap>
                        <!-- <v-text-field v-model="examname" label="考试名称"></v-text-field> -->
                        <v-flex xs12 sm12 md12>
                          <v-text-field v-model="editedExamItem.name" label="考试名称" :readonly="editedExamItem.id>=0"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedExamItem.score1" label="优秀"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedExamItem.score2" label="良好"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedExamItem.score3" label="合格"></v-text-field>
                        </v-flex>
                        <v-flex xs12 sm6 md3>
                          <v-text-field v-model="editedExamItem.score4" label="不合格"></v-text-field>
                        </v-flex>

                        <v-flex xs12 sm12 md6>
                         <el-date-picker v-model="editedExamItem.starttime" type="datetime" value-format="yyyy-MM-dd HH:mm:ss" format="yyyy-MM-dd HH:mm:ss" placeholder="选择开始时间" />
                        </v-flex>
                        <v-flex xs12 sm12 md6>
                          <el-date-picker v-model="editedExamItem.endtime" type="datetime" value-format="yyyy-MM-dd HH:mm:ss" format="yyyy-MM-dd HH:mm:ss" placeholder="选择结束时间" />
                        </v-flex>

                      </v-layout>
                    </v-container>
                  </v-card-text>
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="blue darken-1" flat @click.native="close">取消</v-btn>
                    <v-btn color="blue darken-1" flat @click.native="newExam">保存</v-btn>
                  </v-card-actions>
                </v-card>
              </v-dialog>
            </v-list>
          </v-card>
          
        </v-flex>
        <v-flex lg9 v-if="selected">
          <v-toolbar flat color="white">
            <!-- <v-toolbar-title>{{ selected.name + '(&#60;=' + selected.level1 + '优秀 &#60;=' + selected.level2 + '良好 &#60;=' + selected.level3 + '及格 &#60;=' + selected.level4 + '得分)'}}</v-toolbar-title> -->
            <!--  + '(' + (selected.starttime === undefined ? '时间未设置' : (selected.starttime + '-' + selected.endtime)) + ')' -->
            <v-toolbar-title>{{ selected.name + ' -- [ 优秀(' + selected.score1 + ') 良好(' + selected.score2 + ') 及格(' + selected.score3 + ') 得分(' + selected.score4 + ') ]'}}</v-toolbar-title>
            <v-divider class="mx-2" inset vertical></v-divider>
            <!-- <v-spacer></v-spacer>
            <input type="file" name="importuser" @change="handleFileChange" v-show="selected.state === 1">
            <a href="/static/helpimport.html" target="_blank">导入文件说明</a> -->
          </v-toolbar>
          <v-data-table :headers="selected.state===1 ? headers : headers.slice(0, headers.length-1)" :items="desserts" hide-actions>
            <template slot="items" slot-scope="props">
              <td>{{ props.item.exam_id }}</td>
              <td v-if="selected.state === 1">
               <!--  <v-select :items="lines" v-model="props.item.line_id" item-text="name" item-value="id"></v-select> -->
               {{ lineMap[props.item.line_id].name }}
              </td>
              <td v-else>{{ props.item.line ? props.item.line.name : props.item.line_id }}</td>
              <td>{{ props.item.username }}</td>
              <td>{{ props.item.device_id }}</td>
              <td>{{ props.item.departname }}</td>
              <td v-show="selected.id === active_exam_id">
                <v-icon small class="mr-2" @click="editUserItem(props.item)">edit</v-icon>
              </td>
            </template>
            <template slot="no-data">
              <div></div>
            </template>
          </v-data-table>
          <!-- <div class="text-xs-right">
            <v-btn color="primary" @click="saveExamUser" v-show="desserts.length > 0 && selected.state === 1">保存</v-btn>
          </div> -->

          <v-dialog v-model="userDialog" max-width="800px">
            <v-card>
              <v-card-title>
                <span class="headline">修改用户信息 ({{ editedUserItem.device_id }})</span>
              </v-card-title>
              <v-card-text>
                <v-text-field label="姓名" v-model="editedUserItem.username"></v-text-field>
                <v-text-field label="所属单位" v-model="editedUserItem.departname"></v-text-field>
                <v-select :items="lines" v-model="editedUserItem.line_id" item-text="name" item-value="id"></v-select>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="blue darken-1" flat @click.native="exitUser">取消</v-btn>
                <v-btn color="blue darken-1" flat @click.native="saveUser">保存</v-btn>
              </v-card-actions>
            </v-card>
          </v-dialog>

        </v-flex>
      </v-layout>
    </v-container>
  </div>
</template>

<script>
import jschardet from 'jschardet';

export default {
  data: () => ({
    selected: undefined,
    exams: [],
    active_exam_id: -1,
    lines: [],
    lineMap: {},
    examDialog: false,
    userDialog: false,
    headers: [
      { text: '考试号', value: 'name', sortable: false, align: 'left' },
      { text: '路线号', value: 'calories', sortable: false },
      { text: '姓名', value: 'fat', sortable: false },
      { text: '设备号', value: 'carbs', sortable: false },
      { text: '所属单位', value: 'carbs', sortable: false },
      { text: '动作', value: 'name', sortable: false }
    ],
    desserts: [],
    editedExamIndex: -1,
    editedExamItem: {
      id: -1,
      name: '',
      score1: 0,
      score2: 0,
      score3: 0,
      score4: 0,
      starttime: '',
      endtime: ''
    },
    defaultExamItem: {
      id: -1,
      name: '',
      score1: 0,
      score2: 0,
      score3: 0,
      score4: 0,
      starttime: '',
      endtime: ''
    },
    editedUserItem: {}
  }),
  computed: {
    formTitle () {
      return this.editedExamIndex === -1 ? 'New Item' : 'Edit Item';
    },
  },
  watch: {
    dialog (val) {
      val || this.close();
    },
  },
  created () {
    this.initialize();
  },
  methods: {
    initialize () {
      let that = this;
      that.axios.all([that.axios.get('/api/admin/examline/list?valid=1'), that.axios.get('/api/admin/exams')]).then(that.axios.spread((lines_resp, exams_resp) => {
        console.log(lines_resp);
        console.log(exams_resp);

        if (exams_resp.data.state === 1) {
          that.exams = exams_resp.data.exams;
          that.active_exam_id = exams_resp.data.active_exam_id;
        }

        if (lines_resp.data.state === 1) {
          that.lines = lines_resp.data.exam_line;
          that.lineMap = {};
          that.lines.forEach(item => {
            that.lineMap[item.id] = item;
          });
        }
      }));
    },
    close () {
      this.examDialog = false;
      setTimeout(() => {
        this.editedExamItem = Object.assign({}, this.defaultExamItem);
        this.editedExamIndex = -1;
      }, 300);
    },
    newExam () {
      if (this.editedExamItem.name.trim() === '') {
        alert('名字不能为空！');
      } else if (this.editedExamItem.starttime.trim() === '' || this.editedExamItem.endtime.trim() === '') {
        alert('起止时间必须设置');
      } else {
        let data = 'name=' + encodeURI(this.editedExamItem.name.trim()) +
                   '&score1=' + this.editedExamItem.score1 +
                   '&score2=' + this.editedExamItem.score2 + 
                   '&score3=' + this.editedExamItem.score3 +
                   '&score4=' + this.editedExamItem.score4 +
                   '&starttime=' + this.editedExamItem.starttime +
                   '&endtime=' + this.editedExamItem.endtime;
        if (this.editedExamIndex > -1) {
          // Object.assign(this.desserts[this.editedExamIndex], this.editedExamItem);
          data = data + '&exam_id=' + this.editedExamItem.id;
          this.axios.post('/api/admin/exam', data).then((response) => {
            console.log(response);
            if (response.data.state === 1) {
              this.initialize();
              this.close();
            } else {
              window.alert(response.data.message);
            }
          });
        } else {
          this.axios.post('/api/admin/exam', data).then((response) => {
            console.log(response);
            if (response.data.state === 1) {
              this.initialize();
              this.close();
            } else {
              window.alert(response.data.message);
            }
          });
        }
      }
    },
    examActive (item) {
      this.axios.post('/api/admin/exam', 'exam_id=' + item.id).then((response) => {
        console.log(response.data);
        if (response.data.state === 1) {
          this.active_exam_id = item.id;
          this.selected.state = 2;
        } else {
          alert(response.data.message);
        }
      });
    },
    editExam (item) {
      this.editedExamIndex = this.exams.indexOf(item);
      this.editedExamItem = Object.assign({}, item);
      this.examDialog = true;
    },
    handleFileChange (event) {
      if (typeof (FileReader) !== 'undefined') {
        let that = this;
        let reader = new FileReader();
        reader.readAsArrayBuffer(event.target.files[0]);
        reader.onload = function (evt) {
          let data =  new Uint8Array(evt.target.result);
          let characterTestStr = null;
          for (let index in data) {
            if (index <= 100) {
              characterTestStr += String.fromCharCode(data[index]);
            } else {
              break;
            }
          }
          let codepage = jschardet.detect(characterTestStr.substring(0, 1000)).encoding;
          if (codepage === 'GB2312' || codepage === 'GB18030') {
            codepage = 'GB18030';
          } else if (!(codepage === 'ascii' || codepage === 'UTF-8' || codepage === 'UTF-16BE' || codepage === 'UTF-16LE')) {
            alert('不支持的编码格式:' + codepage + ';你只能使用UTF-8或GB18030(GB2320,GBK)编码格式文件');
            return;
          }

          data = new TextDecoder(codepage).decode(data).split('\r\n');
          let result = [];
          console.log(that.selected);
          data.forEach(item => {
            let tmp = item.split(',');
            if (tmp.length >= 3 && tmp[0].trim() !== '' && tmp[1].trim() !== '' && tmp[2].trim() !== '') {
              result.push({
                exam_id: that.selected.id,
                line_id: that.lines[Math.floor(Math.random() * that.lines.length)].id,
                username: tmp[0],
                device_id: tmp[1],
                departname: tmp[2],
              });
            }
            that.desserts = result;
          });
        };
      } else {
        alert('IE9及以下浏览器不支持，请使用Chrome或Firefox浏览器');
      }
    },
    pathSelected (item) {
      let fileSelect = this.$el.querySelector('input[type=file]');
      if (fileSelect) {
        fileSelect.value = '';
      }
      this.selected = item;
      this.getExamUser();
    },
    getExamUser () {
      this.axios.get('/api/admin/examuser/list/' + this.selected.id).then((response) => {
        console.log(response);
        if (response.data.state === 1) {
          this.desserts = response.data.users;
        }
      });
    },
    saveExamUser () {
      this.axios.post('/api/admin/examuser/list/' + this.selected.id, 'exam_users=' + encodeURI(JSON.stringify(this.desserts))).then((response) => {
        if (response.data.state === 1) {
          window.alert('保存成功');
        } else {
          window.alert(response.data.message);
        }
      });
    },
    editUserItem (item) {
      this.editedUserItem = Object.assign({}, item);
      this.userDialog = true;
    },
    exitUser () {
      this.userDialog = false;
    },
    saveUser () {
      this.axios.post('/api/admin/examuser/list/' + this.selected.id, 'exam_user=' + encodeURI(JSON.stringify(this.editedUserItem))).then((response) => {
        if (response.data.state === 1) {
          this.desserts.forEach(item => {
            if (item.id === response.data.user_info.id) {
              Object.assign(item, response.data.user_info);
            }
          });
          this.userDialog = false;
          window.alert('保存成功');
        } else {
          window.alert(response.data.message);
        }
      });
    }
  }
};
</script>
