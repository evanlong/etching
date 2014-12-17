//
//  LWViewController.m
//  SimulateEtch
//
//  Created by Evan Long on 5/30/13.
//  Copyright (c) 2013 Evan. All rights reserved.
//

/*
 
 */

#import "LWViewController.h"

@interface LWLayerView : NSView

@property (nonatomic, assign) NSPoint center;

@end

@implementation LWLayerView

- (void)_setup
{
    [self setWantsLayer:YES];
}

- (id)initWithFrame:(NSRect)frameRect
{
    self = [super initWithFrame:frameRect];
    if (self)
    {
        [self _setup];
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)aDecoder
{
    self = [super initWithCoder:aDecoder];
    if (self)
    {
        [self _setup];
    }
    return self;
}

- (id)init
{
    self = [super init];
    if (self)
    {
        [self _setup];
    }
    return self;
}

- (NSPoint)center
{
    return NSMakePoint(self.frame.origin.x + self.frame.size.width/2,
                       self.frame.origin.y + self.frame.size.height/2);
}

- (void)setCenter:(NSPoint)center
{
    self.frame = NSMakeRect(center.x - self.frame.size.width/2,
                            center.y - self.frame.size.height/2,
                            self.frame.size.width,
                            self.frame.size.height);
}

@end

///////////////////////////////////////////////////////////////////////////////

@interface LWColorBoxView : LWLayerView
@property (nonatomic, strong) NSColor* backgroundColor;
@end

@implementation LWColorBoxView

- (void)setBackgroundColor:(NSColor *)backgroundColor
{
    _backgroundColor = backgroundColor;
}

- (void)drawRect:(NSRect)dirtyRect
{
    [self.backgroundColor setFill];
    NSRectFill(dirtyRect);
}

@end

///////////////////////////////////////////////////////////////////////////////

@interface LWVector : NSObject
@property (nonatomic, assign) NSPoint direction;
@property (nonatomic, assign) NSInteger distance;
@end

@implementation LWVector
@end

///////////////////////////////////////////////////////////////////////////////

@interface LWSketchView : LWColorBoxView

- (void)drawLeft:(NSInteger)distance;
- (void)drawRight:(NSInteger)distance;
- (void)drawUp:(NSInteger)distance;
- (void)drawDown:(NSInteger)distance;
- (void)flashCursor;

@property (nonatomic, assign) CGFloat scale;
@property (nonatomic, strong) LWColorBoxView* cursor;
@property (nonatomic, strong) NSMutableArray* commandQueue;

@end

@implementation LWSketchView

- (id)init
{
    return [self initWithFrame:NSZeroRect];
}

- (id)initWithFrame:(NSRect)frameRect
{
    self = [super initWithFrame:frameRect];
    if (self)
    {
        self.scale = 2.0;
        self.cursor = [[LWColorBoxView alloc] initWithFrame:NSMakeRect(frameRect.size.width/2,
                                                                       frameRect.size.height-20,
                                                                       self.scale,
                                                                       self.scale)];
        self.cursor.backgroundColor = [NSColor redColor];
        [self addSubview:self.cursor];
        self.commandQueue = [NSMutableArray array];
    }
    return self;
}

- (void)_draw:(NSInteger)distance direction:(NSPoint)direction
{
    // queue path to draw
    LWVector* vector = [[LWVector alloc] init];
    vector.distance = distance;
    vector.direction = direction;
    [self.commandQueue addObject:vector];
    
    // only item so start animating
    if (self.commandQueue.count == 1)
    {
        [self _runCursor];
    }
}

- (void)drawLeft:(NSInteger)distance
{
    [self _draw:distance direction:NSMakePoint(-self.scale, 0)];
}

- (void)drawRight:(NSInteger)distance
{
    [self _draw:distance direction:NSMakePoint(self.scale, 0)];
}

- (void)drawUp:(NSInteger)distance
{
    [self _draw:distance direction:NSMakePoint(0, self.scale)];
}

- (void)drawDown:(NSInteger)distance
{
    [self _draw:distance direction:NSMakePoint(0, -self.scale)];
}

- (void)flashCursor
{
    [NSAnimationContext beginGrouping];
    {
        [[NSAnimationContext currentContext] setDuration:.8];
        
        CGRect oldBonds = self.cursor.bounds;
        self.cursor.bounds = NSMakeRect(0, 0, 100, 100);
        self.cursor.backgroundColor = [NSColor greenColor];
    
        [[NSAnimationContext currentContext] setCompletionHandler:^{
            self.cursor.backgroundColor = [NSColor redColor];
        }];
        
        [[self.cursor animator] setBounds:oldBonds];
    }
    [NSAnimationContext endGrouping];
}

#pragma mark - Private

- (void)_runCursor
{
    if (self.commandQueue.count > 0)
    {
        LWVector* vector = [self.commandQueue objectAtIndex:0];
        [NSAnimationContext beginGrouping];
        {
            [[NSAnimationContext currentContext] setCompletionHandler:^{
                [self.commandQueue removeObjectAtIndex:0];
                [self _runCursor];
            }];

            [[NSAnimationContext currentContext] setDuration:vector.distance/1600.0];
            
            NSRect startFrame = self.cursor.frame;
            NSRect finalFrame = startFrame;
            finalFrame.origin.x += vector.direction.x * vector.distance;
            finalFrame.origin.y += vector.direction.y * vector.distance;

            LWColorBoxView* etchedView = [[LWColorBoxView alloc] initWithFrame:startFrame];
            etchedView.backgroundColor = [NSColor darkGrayColor];
            
            [self addSubview:etchedView];

            [self.cursor removeFromSuperview];
            [self addSubview:self.cursor];

            // check the math on these since we go from center to frame??
            [[self.cursor animator] setFrame:finalFrame];
            
            NSRect finalEtchedFrame = (finalFrame.origin.x > startFrame.origin.x || finalFrame.origin.y > startFrame.origin.y) ? startFrame : finalFrame;
            finalEtchedFrame.size.width = fabs(finalFrame.origin.x - startFrame.origin.x) + self.scale;
            finalEtchedFrame.size.height = fabs(finalFrame.origin.y - startFrame.origin.y) + self.scale;
            [[etchedView animator] setFrame:finalEtchedFrame];
        }
        [NSAnimationContext endGrouping];
    }
}

@end

@interface LWViewController ()
@property (nonatomic, strong) NSScrollView* scrollView;
@property (nonatomic, strong) LWSketchView* sketchView;
@end

@implementation LWViewController

- (void)loadView
{
    self.scrollView = [[NSScrollView alloc] init];
    self.scrollView.hasHorizontalScroller = YES;
    self.scrollView.hasVerticalScroller = YES;
    self.scrollView.backgroundColor = [NSColor darkGrayColor];
    
    self.sketchView = [[LWSketchView alloc] initWithFrame:NSMakeRect(0, 0, 2000, 2000)];
    self.sketchView.backgroundColor = [NSColor blackColor];
    self.scrollView.documentView = self.sketchView;
    [self.scrollView.contentView scrollToPoint:NSMakePoint(350,
                                                           self.sketchView.frame.size.height)];
    self.view = self.scrollView;
}

- (void)keyDown:(NSEvent*)event
{
    if (event.keyCode == 49) // space
    {
        [self.sketchView flashCursor];
    }
}

- (void)simulateEtchASketch:(NSString*)data
{
    NSArray* commands = [data componentsSeparatedByCharactersInSet:[NSCharacterSet newlineCharacterSet]];
    for (NSString* cmd in commands)
    {
        NSArray* commandParts = [cmd componentsSeparatedByCharactersInSet:[NSCharacterSet whitespaceCharacterSet]];
        if (commandParts.count == 2)
        {
            NSString* direction = [commandParts objectAtIndex:0];
            NSInteger distance = [[commandParts objectAtIndex:1] integerValue];
            if ([direction isEqualToString:@"R"])
            {
                [self.sketchView drawRight:distance];
            }
            else if ([direction isEqualToString:@"L"])
            {
                [self.sketchView drawLeft:distance];
            }
            else if ([direction isEqualToString:@"U"])
            {
                [self.sketchView drawUp:distance];
            }
            else if ([direction isEqualToString:@"D"])
            {
                [self.sketchView drawDown:distance];
            }
        }
    }
}

@end
