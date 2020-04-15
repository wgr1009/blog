from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from blog.models import Post, Category, Tag


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'is_nav', 'created_time', 'post_count']
    fields = ['name', 'status', 'is_nav']  # 控制admin后台显示的字段

    # 因为当前所有的用户都可以随意把自己创建的内容改为其他的作者，所以重写save_model方法，把owner这个字段设定为当前的登录用户
    # 如果fields字段设置显示owner，那在后再管理中会看到所有的注册用户名称，但是在创建分类时就算选择其他用户在保存时还是会保存当前的用户
    # 所以安全在owner可以选择不显示，增加分类时自动保存当前登录用户
    def save_model(self, request, obj, form, change):
        """
        :param request:  当前的请求
        :param obj: 当前要保存的对象
        :param form:  form是页面提交过来的表单之后的对象
        :param change: change用于报纸本次保存的数据是新增的还是更新的
        :return:
        """
        obj.owner = request.user  # request.user是当前登录的用户，如果是未登录的情况下，request.user拿到是匿名对象
        return super(CategoryAdmin, self).save_model(request, obj, form, change)

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'status', 'created_time']
    fields = ['name', 'status']

    # 因为当前所有的用户都可以随意把自己创建的内容改为其他的作者，所以重写save_model方法，把owner这个字段设定为当前的登录用户
    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 配置列表页展示字段
    list_display = [
        'title', 'category', 'status', 'created_time', 'operator'
    ]  # operator 自定义一个操作字段

    # 配置那些字段可以作为链接，点击可以进入编辑页面
    list_display_links = []

    list_filter = ['category']  # 显示过滤器，根据那些字段进行过滤
    search_fields = ['title', 'category__name']  # 显示搜索栏，可以根据那些字段进行搜索

    # actions_on_top = True  # 动作相关的配置，是否现在在顶部
    # actions_on_bottom = True  # 动作相关的配置，是否现在在底部

    # 编辑页面
    # save_on_top = True  # 保存，编辑，编辑及新建按钮是否在顶部展示，默认在底部展示

    fields = [
        ('category', 'title'), 'desc', 'status', 'content', 'tag'
    ]

    def operator(self, obj):
        return format_html(
            "<a href='{}'>编辑</a>",
            reverse('admin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = '操作'  # 自定义字段的描述信息

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)


