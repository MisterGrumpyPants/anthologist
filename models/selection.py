from django.db import models
from django.utils.safestring import mark_safe

class Selection(models.Model):
    class Meta:
        ordering = ['-date_entered']
        app_label = 'anthologist'
        
    date_entered = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    text = models.TextField(null=True)
    teaser = models.TextField(null=True)
    comment_intro = models.TextField(blank=True, null=True, help_text="Comment to introduce the selection to the reader.")
    comment_text = models.TextField(blank=True, null=True, help_text="Comment to describe the textual source, proofreading, editing, &c.")
    source = models.ForeignKey('Source')
    excerpt = models.BooleanField(help_text="Is the selection an excerpt (checked) or a complete text (unchecked)?")
    selection_title = models.CharField(max_length=100, blank=True, null=True,
                                       help_text="If desired, add a title more suitable for the excerpt than the source's title. Necessary if source has no section_title.")
    genres = models.ManyToManyField('Tag', related_name='genre_selections', blank=True)
    contexts = models.ManyToManyField('Tag', related_name='context_selections', blank=True)
    topics = models.ManyToManyField('Tag', related_name='topic_selections', blank=True)
    styles= models.ManyToManyField('Tag', related_name='style_selections', blank=True)
    slug = models.SlugField(unique=True)
    stylesheet = models.SlugField(blank=True, null=True, help_text="If this selection requires its own accompanying stylesheet, specify the filename. Use the slug, unless there's a good reason. Ensure the file is in static/anthologist/css/selection-specific/.")
    
    def shortened_passage(self):
        return r'"' + self.text[:70] + r'..."' 
    
    def author(self):
        return self.source.author
    
    def source_display(self):
        title = self.source.full_title()
        return title
    
    def __unicode__(self):
        if self.selection_title:
            return self.selection_title
        else:
            return self.source.section_title
        
    def class_name(self):
        return 'Selection'
        #Used to distinguish Announcements from Selections on the homepage, so that the lists can be merged
        #but each instance is given a template corresponding to its model (not the same one for every instance).

        
    def toJSON(self):
        return dict(
            id = self.id,
            date_entered = self.date_entered.strftime("%d %B %Y, %H:%M"),
            date_entered_microdata = self.date_entered.isoformat(),
            date_modified = self.date_modified.strftime("%d %B %Y, %H:%M"),
            date_modified_microdata = self.date_entered.isoformat(), 
            #text is excluded because this dictionary is only called for tables of contents
            teaser = self.teaser,
            comment_intro = self.comment_intro,
            comment_text = self.comment_text,
            excerpt = self.excerpt,
            selection_title = self.selection_title,
            slug = self.slug,
            shortened_passage = self.shortened_passage(),
            source_display = self.source_display(),
            class_name = self.class_name()      
        )
    
    def closure(self):
        selection = self.toJSON()
        selection['source'] = self.source.closure()
        selection['nations'] = [ nation.toJSON() for nation in self.source.author.nations.all() ]
        selection['language'] = [ self.source.language.toJSON() ]
        selection['forms'] = [ form.toJSON() for form in self.source.forms.all() ]
        selection['contexts'] = [ context.toJSON() for context in self.contexts.all() ]
        selection['genres'] = [ genre.toJSON() for genre in self.genres.all() ]
        selection['topics'] = [ topic.toJSON() for topic in self.topics.all() ]
        selection['styles'] = [ style.toJSON() for style in self.styles.all() ]
        return selection